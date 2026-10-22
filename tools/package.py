#!/usr/bin/env python3
"""Create a checksummed development archive; never emits a bootable image."""
import argparse,hashlib,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--shim-image",type=Path,default=ROOT/"out/bootshim/Image")
 ap.add_argument("--xnu-kernel",type=Path); ap.add_argument("--payload",type=Path); ap.add_argument("--ramdisk",type=Path)
 ap.add_argument("--output",type=Path,default=ROOT/"dist/a03s-dev-bundle.tar.gz")
 a=ap.parse_args(); items=[("board.json",ROOT/"board.json"),("shim/Image",a.shim_image)]
 for name,p in (("artifacts/xnu-kernel",a.xnu_kernel),("artifacts/payload.bin",a.payload),("artifacts/ramdisk.img",a.ramdisk)):
  if p is not None: items.append((name,p))
 missing=[str(p) for _,p in items if not p.is_file()]
 if missing: ap.error("missing required input(s): "+", ".join(missing))
 manifest={"kind":"a03s-development-bundle","target":"Samsung Galaxy A03s SM-A037F / MediaTek MT6765","components":[{"path":n,"bytes":p.stat().st_size,"sha256":digest(p)} for n,p in items],"bootable":False,"xnu_handoff_implemented":False,"hardware_tested":False,"note":"Artifact archive only; not an Android/Samsung boot image. Do not flash."}
 a.output.parent.mkdir(parents=True,exist_ok=True); mp=a.output.parent/"build-manifest.json"
 mp.write_text(json.dumps(manifest,indent=2)+"\\n")
 try:
  with tarfile.open(a.output,"w:gz") as t:
   for name,p in items: t.add(p,arcname=name,recursive=False)
   t.add(mp,arcname="build-manifest.json",recursive=False)
 finally: mp.unlink(missing_ok=True)
 print(json.dumps({"output":str(a.output),"components":len(items),"bootable":False},indent=2))
if __name__=="__main__": main()
