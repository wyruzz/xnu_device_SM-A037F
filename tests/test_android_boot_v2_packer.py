# SPDX-License-Identifier: MIT
"""Tests for the generic Android boot v2 container writer."""
import importlib.util
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pack_android_boot_v2", ROOT / "tools" / "pack_android_boot_v2.py")
packer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packer)
INSPECT_SPEC = importlib.util.spec_from_file_location("inspect_stock_boot", ROOT / "tools" / "inspect_stock_boot.py")
inspector = importlib.util.module_from_spec(INSPECT_SPEC)
INSPECT_SPEC.loader.exec_module(inspector)


class AndroidBootV2PackerTests(unittest.TestCase):
    def build(self, **kwargs):
        options = dict(kernel=b"ARM64-SHIM", ramdisk=b"EMPTY-CPIO", dtb=b"\xd0\x0d\xfe\xed" + bytes(36),
                       kernel_addr=0x40080000, ramdisk_addr=0x51b00000,
                       tags_addr=0x47880000, dtb_addr=0x48000000)
        options.update(kwargs)
        return packer.pack(**options)

    def test_round_trip_header_and_sections(self):
        image = self.build(cmdline="console=ttyS0")
        result = inspector.inspect(image)
        self.assertEqual(result["header_version"], 2)
        self.assertEqual(result["page_size"], 2048)
        self.assertEqual(result["kernel_size"], len(b"ARM64-SHIM"))
        self.assertEqual(result["ramdisk_size"], len(b"EMPTY-CPIO"))
        self.assertEqual(result["dtb_size"], 40)
        self.assertEqual(result["cmdline"], "console=ttyS0")
        self.assertEqual(image[:8], b"ANDROID!")
        self.assertEqual(struct.unpack_from("<I", image, 1644)[0], 1660)

    def test_rejects_empty_sections(self):
        with self.assertRaises(ValueError):
            self.build(kernel=b"")

    def test_rejects_bad_page_size(self):
        with self.assertRaises(ValueError):
            self.build(page_size=3000)

    def test_rejects_non_ascii_cmdline(self):
        with self.assertRaises(UnicodeError):
            self.build(cmdline="тест")


if __name__ == "__main__":
    unittest.main()
