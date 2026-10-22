# SM-A037F unified port plan

## This branch

- Places the diagnostic shim sources in `shim/` with source provenance retained.
- Adds a device-local board mirror while keeping root `board.json` canonical.
- Makes XNU/patch status explicit instead of borrowing target-specific patches.
- Adds host validation and a checksummed development bundle that explicitly marks itself non-bootable.

## Evidence-backed observations

- Samsung Galaxy A03s SM-A037F, MediaTek MT6765V/WB, Cortex-A53.
- Captured DT reports 4 GiB DRAM from `0x40000000`; reserved regions still need runtime analysis.
- Stock boot header observed as Android v2 with 2048-byte pages; this does not establish Samsung/MediaTek framing for a new image.
- UART base `0x11002000` is observed in captured DT but not verified on hardware.

## Blockers

- No A03s XNU kernel or validated patch series.
- No verified ADT generator or XNU memory map.
- No confirmed Samsung/MT6765 boot-image packer or proven reversible test path.
- UART output and shim entry state not yet confirmed on-device.
- No XNU handoff or end-to-end hardware test.

## Next steps

1. Keep observed facts and hypotheses separately labelled.
2. Expand host tests around FDT parsing and metadata validation.
3. Inspect runtime DTB and stock image metadata without modifying storage.
4. Do not enable image emission until the format is confirmed by evidence.
