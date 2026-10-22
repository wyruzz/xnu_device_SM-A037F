# Samsung Galaxy A03s SM-A037F porting data

This file records measured/observed values for the target device. It deliberately
separates evidence from assumptions inherited from the Benesse MT8167 donor.

## Hardware and memory

- Model: Samsung SM-A037F.
- SoC: MediaTek MT6765V/WB.
- CPU family: ARM Cortex-A53.
- Captured physical DRAM span: `0x40000000..0x140000000` (4 GiB, end-exclusive).
- Captured FDT size: 195,626 bytes.

The span is not all automatically available to XNU. Parse the live DTB and
exclude fixed reservations, dynamic reservation allocations, secure-world
regions, and any other ranges owned by firmware before selecting a managed
physical window. Do not reuse the donor board's `0x60000000` managed window
without checking the A03s runtime map.

## UART

The captured tree contains `serial@11020000` with `reg = <0 0x11002000 0 0x1000>`.
For register access, the observed base is therefore `0x11002000`; the node
unit-address is not the same value. A second node `serial@11030000` has base
`0x11003000`.

The captured properties do not establish a usable baud rate, pinmux, or that
the bootloader leaves either UART enabled and routed. Keep UART output marked
unverified until a live capture confirms it.

## Stock boot image

Observed header fields from the stock boot image:

| Field | Value |
|---|---:|
| Header version | 2 |
| Page size | 2048 bytes |
| Kernel size | 12,409,268 bytes |
| Kernel address | `0x40080000` |
| Ramdisk size | 1,448,717 bytes |
| Ramdisk address | `0x51b00000` |
| Second-stage size | 0 |
| Tags address | `0x47880000` |

These are stock-image observations, **not** a validated load contract for an
XNU image or this project's bootshim. The extracted stock kernel is an ARM64
Linux Image. Do not replace it with a raw shim image or assume the donor's
Android v0 + MediaTek section-header wrapper is correct for this device.
The boot chain's actual image requirements must be established before packing
a test image.

## Partitions observed

- boot: `/dev/block/mmcblk0p37`
- dtbo: `/dev/block/mmcblk0p12`
- vbmeta: `/dev/block/mmcblk0p13`
- recovery: `/dev/block/mmcblk0p38`

No GPT layout is proposed here. In particular, the donor `layouts/xnu.json`
changes must not be applied to the A03s.

## Reserved memory

The captured tree includes these dynamic reservation requests:

| Purpose | Requested size |
|---|---:|
| SSMR/CMA | `0x18000000` |
| Wi-Fi | `0x300000` |
| SSPM shared memory | `0x510000` |
| Connectivity | `0x440000` |
| SCP shared memory | `0x300000` |
| ION heap | `0x5000` |

Their alignment and allocation-range constraints are in the captured data.
These sizes are requests, not proof of assigned fixed bases. A port must inspect
the runtime DTB, account for any bootloader fixups, and construct a non-overlap
memory map before entering XNU.

## What remains device-specific

1. Preserve/extract the full live A03s DTB; the property-file snapshot is not a
   source DTS and must not be replaced by the donor MT8167 DTS.
2. Confirm the MT6765 boot image framing and the path used to load a diagnostic
   shim while preserving the stock boot chain.
3. Validate the actual shim entry exception level, registers, stack, and live
   DTB pointer on-device.
4. Only then select the XNU load/managed-memory ranges and implement handoff.

Until these are done, inherited MT8167 packaging and GPT tools are donor
reference code only, not an A03s build recipe.
