#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read Android boot header v2 metadata without modifying the image."""
import argparse
import json
import struct
from pathlib import Path


def align(value, boundary):
    return (value + boundary - 1) // boundary * boundary


def inspect(blob):
    if len(blob) < 2048 or blob[:8] != b"ANDROID!":
        raise ValueError("not an Android boot image (missing ANDROID! header)")
    fields = struct.unpack_from("<10I", blob, 8)
    kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page_size, version, os_version = fields
    if version != 2:
        raise ValueError(f"expected Android header version 2, found {version}")
    if page_size < 512 or page_size > 65536 or page_size & (page_size - 1):
        raise ValueError(f"invalid page size: {page_size}")
    if len(blob) < page_size:
        raise ValueError("truncated boot header page")
    recovery_dtbo_size = struct.unpack_from("<I", blob, 1632)[0]
    recovery_dtbo_offset = struct.unpack_from("<Q", blob, 1636)[0]
    header_size = struct.unpack_from("<I", blob, 1644)[0]
    dtb_size = struct.unpack_from("<I", blob, 1648)[0]
    dtb_addr = struct.unpack_from("<Q", blob, 1652)[0]
    if header_size < 1660 or header_size > page_size:
        raise ValueError(f"invalid v2 header_size: {header_size}")

    offsets = {}
    cursor = page_size
    for name, size in (("kernel", kernel_size), ("ramdisk", ramdisk_size),
                       ("second", second_size), ("recovery_dtbo", recovery_dtbo_size),
                       ("dtb", dtb_size)):
        offsets[name] = {"offset": cursor if size else None, "size": size}
        if size:
            end = cursor + size
            if end > len(blob):
                raise ValueError(f"{name} extends beyond file ({end} > {len(blob)})")
            cursor = align(end, page_size)
    if recovery_dtbo_size and recovery_dtbo_offset != offsets["recovery_dtbo"]["offset"]:
        offsets["recovery_dtbo"]["header_offset_matches_layout"] = False
    elif recovery_dtbo_size:
        offsets["recovery_dtbo"]["header_offset_matches_layout"] = True

    cmdline = blob[64:576].split(bytes([0]), 1)[0].decode("ascii", "replace")
    extra = blob[608:1632].split(bytes([0]), 1)[0].decode("ascii", "replace")
    return {
        "file_size": len(blob),
        "header_version": version,
        "header_size": header_size,
        "page_size": page_size,
        "kernel_size": kernel_size,
        "kernel_addr": f"0x{kernel_addr:x}",
        "ramdisk_size": ramdisk_size,
        "ramdisk_addr": f"0x{ramdisk_addr:x}",
        "second_size": second_size,
        "second_addr": f"0x{second_addr:x}",
        "tags_addr": f"0x{tags_addr:x}",
        "os_version_raw": f"0x{os_version:x}",
        "recovery_dtbo_size": recovery_dtbo_size,
        "recovery_dtbo_offset_header": recovery_dtbo_offset,
        "dtb_size": dtb_size,
        "dtb_addr": f"0x{dtb_addr:x}",
        "cmdline": cmdline,
        "extra_cmdline": extra,
        "sections": offsets,
        "note": "Metadata inspection only; does not validate Samsung/MediaTek vendor framing or prove the image is safe to boot."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="path to an extracted stock boot image")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    try:
        result = inspect(args.image.read_bytes())
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
