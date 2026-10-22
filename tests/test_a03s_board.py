# SPDX-License-Identifier: MIT
"""Regression tests for the SM-A037F evidence record and donor-build guard."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class A03sBoardTests(unittest.TestCase):
    def test_board_identity_and_memory_span(self):
        board = json.loads((ROOT / "board.json").read_text())
        self.assertEqual(board["model"], "Samsung Galaxy A03s SM-A037F")
        self.assertEqual(board["soc"], "MediaTek MT6765V/WB (Helio P35 family)")
        evidence = board["evidence"]
        base = int(evidence["memory_base"], 0)
        size = int(evidence["memory_size"], 0)
        end = int(evidence["memory_end_exclusive"], 0)
        self.assertEqual(base + size, end)
        self.assertEqual(size, 4 * 1024**3)

    def test_stock_boot_header_is_recorded_as_evidence(self):
        boot = json.loads((ROOT / "board.json").read_text())["evidence"]["boot_image"]
        self.assertEqual(boot["header_version"], 2)
        self.assertEqual(boot["page_size"], 2048)
        self.assertEqual(boot["kernel_addr"], "0x40080000")
        self.assertEqual(boot["ramdisk_addr"], "0x51b00000")

    def test_uart_uses_reg_base_not_node_unit_address(self):
        uart = json.loads((ROOT / "board.json").read_text())["evidence"]["uart"]
        self.assertEqual(uart["node"], "serial@11020000")
        self.assertEqual(uart["reg_base"], "0x11002000")
        self.assertIsNone(uart["baud_rate"])

    def test_a04br3_gpt_and_memory_are_not_promoted_as_a03s_data(self):
        board = json.loads((ROOT / "board.json").read_text())
        self.assertEqual(board["port_status"]["device_specific_dts"],
                         "not yet available as a source DTS; do not substitute the MT8167 donor DTS")
        self.assertEqual(board["port_status"]["xnu_handoff"], "not implemented or hardware-tested")


if __name__ == "__main__":
    unittest.main()
