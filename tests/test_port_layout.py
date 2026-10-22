import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PortLayoutTests(unittest.TestCase):
 def test_layout_files(self):
  for p in ("shim/start.S","shim/shim.c","device/board.json","xnu/README.md","xnu/patches/README.md","tools/package.py"):
   with self.subTest(path=p): self.assertTrue((ROOT/p).is_file())
 def test_board_validator(self): subprocess.run([sys.executable,str(ROOT/"tools/validate_board.py")],check=True)
 def test_xnu_source_pin_is_valid(self): subprocess.run([sys.executable,str(ROOT/"tools/validate_sources.py")],check=True)
 def test_bundle_is_nonbootable(self):
  s=(ROOT/"tools/package.py").read_text(); self.assertIn('"bootable":False',s); self.assertIn('"xnu_handoff_implemented":False',s)
if __name__=="__main__": unittest.main()
