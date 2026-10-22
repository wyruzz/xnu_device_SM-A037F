# XNU source baseline — SM-A037F

The initial upstream baseline is Apple's public XNU source at tag [`xnu-8796.141.3`](https://github.com/apple-oss-distributions/xnu/tree/xnu-8796.141.3).

- Tag: `xnu-8796.141.3`
- Peeled commit: `1b191cb58250d0705d8a51287127505aa4bc0789`
- Annotated tag object: `f625db25f47631424dc62ac1c3414b6e530f7e8a`
- Tag verification: GitHub reports the tag as unsigned; the commit is pinned for reproducibility, not cryptographic authenticity.
- Lock entry: [`sources.lock.json`](../sources.lock.json)

## What this baseline means

This pins source provenance only. It does not mean that this XNU revision supports the MediaTek MT6765, Samsung SM-A037F, its interrupt controller, timer, memory map, device tree, storage, or boot protocol. The reference source tree describes generic XNU components and build configuration, but platform support must be established independently.

## Porting rules

1. Keep upstream source immutable and record any local changes as small, reviewable patches under `xnu/patches/`.
2. Do not copy patches from unrelated iPhone or MT8167 targets without checking each platform assumption.
3. First validate source acquisition, pinned revision, toolchain prerequisites, and a reproducible baseline build in CI. A successful generic ARM64 compile is not evidence that the kernel can run on A03s.
4. Keep the existing diagnostic shim status unchanged: XNU handoff is not implemented or hardware-tested.

No XNU build artifact, payload, ramdisk, or A03s boot image is included by this source pin.
