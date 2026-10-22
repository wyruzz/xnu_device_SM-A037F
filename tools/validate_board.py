#!/usr/bin/env python3
"""Validate the SM-A037F board record and its uncertainty labels."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
b=json.loads((ROOT/"board.json").read_text())
assert b["model"]=="Samsung Galaxy A03s SM-A037F"
assert "MT6765" in b["soc"] and b["cpu"]=="ARM Cortex-A53"
e=b["evidence"]
assert e["memory_base"]=="0x40000000" and e["memory_size"]=="0x100000000"
assert e["boot_image"]["header_version"]==2 and e["boot_image"]["page_size"]==2048
assert "not verified" in e["uart"]["status"]
s=b["port_status"]
assert s["xnu_handoff"]=="not implemented or hardware-tested"
assert s["boot_image_packaging"]=="not yet adapted/validated for the A03s MT6765 boot chain"
assert json.loads((ROOT/"device/board.json").read_text())==b, "board mirror drift"
print("SM-A037F board metadata OK; unverified values remain labelled")
