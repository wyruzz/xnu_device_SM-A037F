# Samsung Galaxy A03s SM-A037F — experimental XNU port

**Target:** Samsung Galaxy A03s SM-A037F, MediaTek MT6765V/WB.  
**Status:** source adaptation and early diagnostics only. No A03s XNU handoff has
been implemented or hardware-verified.

This repository was forked from the Benesse TAB-A04-BR3 (MT8167) project. The
donor's packaging and kernel integration are not valid for A03s by default.
The old DTS, bootopt, load assumptions, board-specific kernel switches, and
GPT layouts are retained only as donor reference; do not use them to produce
or flash an A03s image.

## Unified repository layout

This tree follows the broad layout of [iOS-MT6765](https://github.com/wyruzz/iOS-MT6765), adapted conservatively for SM-A037F:

- `shim/`: diagnostic AArch64 shim sources copied from [xnu_bootshim_SM-A037F](https://github.com/wyruzz/xnu_bootshim_SM-A037F).
- `device/board.json`: mirror of recorded board facts; root `board.json` remains canonical.
- `layouts/`: planning metadata, not a validated physical memory map or boot-image recipe.
- `tools/package.py`: checksummed development archive only, never a Samsung boot image.
- `xnu/`: pinned upstream XNU baseline (`xnu-8796.141.3`) and porting notes; no A03s kernel or patch series is claimed ready.

Build the diagnostic shim with `CROSS_COMPILE=aarch64-linux-gnu- SHIM_OUT="$PWD/out/bootshim" ./shim/build.sh`. Run `python3 tools/validate_board.py` and `python3 -m unittest discover -s tests -p 'test_port_layout.py'` for host-side checks. The inherited MT8167 DTS/kernel/packer are not valid for MT6765 by default. Missing XNU, payload, ramdisk, and verified image framing remain blockers; do not flash the diagnostic artifact.

## Pinned XNU source baseline

The repository now pins Apple XNU tag `xnu-8796.141.3` to commit `1b191cb58250d0705d8a51287127505aa4bc0789` in `sources.lock.json`. The upstream tag is unsigned. This is a reproducible source reference, not a claim of MT6765 support or a built kernel. See [xnu/README.md](xnu/README.md). CI validates the lock metadata; it does not yet build XNU.

## Source repositories

- **Device configuration and future packaging:** this repository.
- **A03s diagnostic bootshim:** https://github.com/wyruzz/xnu_bootshim_SM-A037F
- **Kernel source:** the kernel entry in sources.lock.json is still the donor
  A04BR3 kernel and is explicitly **not an A03s kernel**.

sources.lock.json pins the A03s bootshim commit. The donor kernel entry is
retained only so its provenance is explicit; this build must not package it as
an A03s kernel.

## Recorded device evidence

See [board.json](board.json) and
[docs/SM-A037F-PORTING-DATA.md](docs/SM-A037F-PORTING-DATA.md). The current
capture reports 4 GiB of DRAM starting at 0x40000000, a stock Android boot
header version 2 with 2048-byte pages, and the stock kernel load address
0x40080000. These are observations, not a validated XNU load layout.

The UART register base captured for serial@11020000 is 0x11002000.
Actual UART output/pin routing is not verified. The property snapshot is not a
source DTS; do not replace it with the donor MT8167 DTS.

## Build the diagnostic shim (not a boot image)

On macOS/Hackintosh, install Python 3, Git, and an AArch64 bare-metal GNU
toolchain that provides aarch64-elf-gcc, aarch64-elf-readelf,
aarch64-elf-ld, and aarch64-elf-objcopy (or configure CROSS_COMPILE to your
toolchain prefix). Then run:

    git clone https://github.com/wyruzz/xnu_device_SM-A037F.git device
    git clone https://github.com/wyruzz/xnu_bootshim_SM-A037F.git bootshim
    git -C bootshim checkout 02bd4c945bd1e070dd0ce406ed97c9abad6c4ad8
    CROSS_COMPILE=aarch64-elf- SHIM_OUT="$PWD/out/bootshim" ./bootshim/build-macos.sh

The script emits a raw ARM64 Linux Image-format container at
out/bootshim/Image. That file is a diagnostic shim payload, **not a complete
Samsung boot image** and must not be flashed directly. The shim currently logs
entry state if its UART works and stops; it does not transition exception
levels or launch XNU.

## Inspect the stock boot image

The read-only inspector records the standard Android v2 header and calculated
section offsets from an extracted stock boot image. It does not modify the
image and does not claim to decode any additional Samsung/MediaTek vendor
framing:

    python3 tools/inspect_stock_boot.py /path/to/stock-boot.img --json

Use the result to compare the real image with the values recorded in board.json.
If the tool rejects the image, preserve the original file and investigate its
header/layout rather than attempting to repack it.

## Why the image packager is disabled

The inherited tools/build.py emits Android v0 + MediaTek section framing for
MT8167, uses the donor DTS and donor command-line prefix, and contains donor
kernel assumptions. The A03s stock image is header version 2. We have not yet
established the complete Samsung/MT6765 image framing and loading path required
to create a valid test image. The builder therefore intentionally refuses to
emit an A03s image.

## Next implementation steps

1. Preserve and inspect the full A03s runtime DTB, including bootloader fixups.
2. Confirm the A03s boot-image layout and a reversible way to launch a diagnostic
   payload without modifying GPT or replacing the only recovery path.
3. Build and test the diagnostic shim, then confirm its entry state over UART
   or another observable channel.
4. Derive a non-overlapping physical-memory map from the live DTB and reserved
   regions before implementing the XNU handoff.

No GPT changes or storage writes are required for the current diagnostic stage.
