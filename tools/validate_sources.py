#!/usr/bin/env python3
"""Check that upstream source revisions are pinned to immutable Git commits."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/"sources.lock.json").read_text())
xnu=lock["xnu"]
assert xnu["repository"]=="https://github.com/apple-oss-distributions/xnu"
assert xnu["tag"]=="xnu-8796.141.3"
assert xnu["commit"]=="1b191cb58250d0705d8a51287127505aa4bc0789"
assert xnu["tag_object"]=="f625db25f47631424dc62ac1c3414b6e530f7e8a"
assert xnu["tag_signature"]=="unsigned"
assert "not yet built for SM-A037F" in xnu["role"]
shim=lock["bootshim"]
assert len(shim["commit"])==40
print(f"XNU source pin OK: {xnu['tag']} -> {xnu['commit']} (unsigned tag)")
