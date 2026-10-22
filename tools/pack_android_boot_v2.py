#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Create a generic Android boot-image v2 container for offline format tests.

This is NOT a Samsung/MediaTek packager and does not certify an image as bootable.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

MAGIC = b"ANDROID!"
V2_HEADER_SIZE = 1660
DEFAULT_PAGE_SIZE = 2048
MAX_PAGE_SIZE = 65536


def align(value, boundary):
    return (value + boundary - 1) // boundary * boundary


def read_input(path, name, required=True):
    if path is None:
        if required:
            raise ValueError(f"missing required {name}")
        return b""
    data = path.read_bytes()
    if required and not data:
        raise ValueError(f"{name} must not be empty")
    return data


def pack(kernel, ramdisk, dtb, *, kernel_addr, ramdisk_addr, tags_addr,
         dtb_addr, page_size=DEFAULT_PAGE_SIZE, cmdline=""):
    """Build standard Android boot header v2 sections with caller-supplied inputs."""
    if not kernel:
        raise ValueError("kernel/shim payload must not be empty")
    if not ramdisk:
        raise ValueError("ramdisk must not be empty; use an explicit empty cpio archive")
    if not dtb:
        raise ValueError("DTB must not be empty")
    if page_size < 2048 or page_size > MAX_PAGE_SIZE or page_size & (page_size - 1):
        raise ValueError("page size must be a power of two from 2048 through 65536")
    if len(cmdline.encode("ascii", "strict")) >= 512:
        raise ValueError("cmdline must fit in the 512-byte command-line field")
    for name, value in (("kernel_addr", kernel_addr), ("ramdisk_addr", ramdisk_addr),
                         ("tags_addr", tags_addr), ("dtb_addr", dtb_addr)):
        if not 0 <= value <= 0xffffffff and name != "dtb_addr":
            raise ValueError(f"{name} must fit in 32 bits")
        if not 0 <= value <= 0xffffffffffffffff:
            raise ValueError(f"{name} must be non-negative")

    header = bytearray(page_size)
    header[:8] = MAGIC
    # Android boot_img_hdr v0 common fields.
    struct.pack_into("<10I", header, 8, len(kernel), kernel_addr, len(ramdisk),
                     ramdisk_addr, 0, 0, tags_addr, page_size, 2, 0)
    header[64:64 + len(cmdline)] = cmdline.encode("ascii")
    # v1/v2 extension fields. No recovery DTBO is included.
    struct.pack_into("<I", header, 1632, 0)       # recovery_dtbo_size
    struct.pack_into("<Q", header, 1636, 0)       # recovery_dtbo_offset
    struct.pack_into("<I", header, 1644, V2_HEADER_SIZE)
    struct.pack_into("<I", header, 1648, len(dtb))
    struct.pack_into("<Q", header, 1652, dtb_addr)

    image = bytearray(header)
    image.extend(kernel)
    image.extend(bytes(align(len(image), page_size) - len(image)))
    image.extend(ramdisk)
    image.extend(bytes(align(len(image), page_size) - len(image)))
    image.extend(dtb)
    # Android boot image ID: SHA-1(section bytes + little-endian uint32 size), padded to 32 bytes.
    digest = hashlib.sha1()
    for section in (kernel, ramdisk, b"", b"", dtb):
        digest.update(section)
        digest.update(struct.pack("<I", len(section)))
    image[576:608] = digest.digest().ljust(32, b"\0")
    return bytes(image)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", type=Path, required=True, help="ARM64 Image-format shim payload")
    parser.add_argument("--ramdisk", type=Path, required=True, help="ramdisk cpio/gzip payload; format is not validated")
    parser.add_argument("--dtb", type=Path, required=True, help="device tree blob")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kernel-addr", type=lambda x: int(x, 0), required=True)
    parser.add_argument("--ramdisk-addr", type=lambda x: int(x, 0), required=True)
    parser.add_argument("--tags-addr", type=lambda x: int(x, 0), required=True)
    parser.add_argument("--dtb-addr", type=lambda x: int(x, 0), required=True)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--cmdline", default="")
    args = parser.parse_args()
    try:
        kernel = read_input(args.kernel, "kernel")
        ramdisk = read_input(args.ramdisk, "ramdisk")
        dtb = read_input(args.dtb, "DTB")
        image = pack(kernel, ramdisk, dtb, kernel_addr=args.kernel_addr,
                     ramdisk_addr=args.ramdisk_addr, tags_addr=args.tags_addr,
                     dtb_addr=args.dtb_addr, page_size=args.page_size, cmdline=args.cmdline)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(image)
        manifest = {
            "format": "generic-android-boot-header-v2",
            "output": str(args.output),
            "bytes": len(image),
            "kernel_bytes": len(kernel),
            "ramdisk_bytes": len(ramdisk),
            "dtb_bytes": len(dtb),
            "page_size": args.page_size,
            "kernel_addr": hex(args.kernel_addr),
            "ramdisk_addr": hex(args.ramdisk_addr),
            "tags_addr": hex(args.tags_addr),
            "dtb_addr": hex(args.dtb_addr),
            "sha256": hashlib.sha256(image).hexdigest(),
            "hardware_tested": False,
            "samsung_mtk_compatible": False,
            "bootable_claim": False,
        }
        args.output.with_suffix(args.output.suffix + ".json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, indent=2))
    except (OSError, ValueError, UnicodeError, struct.error) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
