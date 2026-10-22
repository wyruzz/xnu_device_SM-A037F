# SPDX-License-Identifier: MIT
import struct
import unittest
from tools.inspect_stock_boot import inspect


class InspectStockBootTests(unittest.TestCase):
    def make_v2(self):
        page = 2048
        blob = bytearray(page + 4 + (page - 4) + 3)
        blob[:8] = b"ANDROID!"
        struct.pack_into("<10I", blob, 8,
                         4, 0x40080000, 3, 0x51B00000,
                         0, 0, 0x47880000, page, 2, 0)
        blob[64:64 + len(b"console=ttyS0\0")] = b"console=ttyS0\0"
        struct.pack_into("<I", blob, 1644, 1660)
        blob[page:page + 4] = b"KERN"
        blob[page * 2:page * 2 + 3] = b"RAM"
        return bytes(blob)

    def test_reads_v2_header_and_offsets(self):
        result = inspect(self.make_v2())
        self.assertEqual(result["header_version"], 2)
        self.assertEqual(result["kernel_addr"], "0x40080000")
        self.assertEqual(result["ramdisk_addr"], "0x51b00000")
        self.assertEqual(result["cmdline"], "console=ttyS0")
        self.assertEqual(result["sections"]["kernel"]["offset"], 2048)
        self.assertEqual(result["sections"]["ramdisk"]["offset"], 4096)

    def test_rejects_donor_v0_image(self):
        blob = bytearray(self.make_v2())
        struct.pack_into("<I", blob, 40, 0)
        with self.assertRaisesRegex(ValueError, "version 2"):
            inspect(bytes(blob))


if __name__ == "__main__":
    unittest.main()
