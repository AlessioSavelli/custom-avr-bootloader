# Custom AVR Bootloader Project

This repository contains a complete workflow for building, installing, and updating a custom bootloader for an ATmega32U4-based board (the same class of hardware as the Arduino Leonardo/Micro family).

The project is split into three main parts:

1. **Bootloader firmware** under `bootloader/`
   - A LUFA-based USB bootloader for the ATmega32U4.
   - Handles USB communication, command parsing, memory programming, and application launch.

2. **Toolchain utilities** under `toolchain/`
   - Python scripts to compile the bootloader and application, install the programmer, upload firmware, and manage COM port selection.
   - Also includes the low-level protocol logic used to talk to the bootloader.

3. **Firmware updater GUI** under `firmware-updater/`
   - A small PyWebView-based desktop application that lets a user load an encrypted firmware file and update the device through the bootloader.

---

## Changes in this fork (security & size)

This fork hardens the firmware encryption and reworks the bootloader so that a
**real block cipher fits in the same 4 KB boot section** that previously barely
held a trivial cipher.

### Stronger encryption
- **Before:** XOR with a repeating key, where the key was the trivial sequence
  `0x00, 0x01, … 0x7F`. This is effectively a Vigenère cipher: the first byte was
  left in clear (key starts at `0x00`), there was no diffusion, and identical
  plaintext pages produced identical ciphertext.
- **After:** **Speck 32/64 in CTR mode** — a genuine lightweight block cipher
  (64-bit secret key, 22 rounds). Each flash page is encrypted with a **per-page
  nonce** (the page address), so identical pages no longer map to identical
  ciphertext and there is no keystream reuse. The page address now travels in
  clear (it is the public CTR nonce); only the 128 data bytes are encrypted.
- **Validated three ways:** against the official Speck32/64 test vector, byte-for-byte
  between the C firmware and the Python toolchain, and by running the AVR-compiled
  cipher inside the `avr-gdb` simulator — all producing identical output.

### Memory footprint (ATmega32U4, 4 KB boot section — a hard ceiling)
| Metric | Before (XOR) | After (Speck) |
|--------|-------------:|--------------:|
| Flash `Program` | 4076 B | **4088 B** |
| RAM (`.data + .bss`) | 308 B | **174 B** (−43 %) |
| Cipher strength | repeating-key XOR | real block cipher (Speck32/64-CTR) |

The cipher itself grew (~304 B → ~416 B of code + key), but that cost was paid for
by size optimizations so the net flash change is only +12 B:
- **LTO** (link-time optimization) enabled: ≈ −132 B;
- Speck core shrunk from 488 B → 408 B (on-the-fly key schedule, shift-register
  instead of `l[i % 3]`, byte-swap rotations);
- bootloader **timer changed from 32-bit to 16-bit** (the 60 s timeout fits in 16
  bits): ≈ −150 B and most of the RAM saving;
- secret key shrunk from 128 B to 8 B.

> ⚠️ **To deploy:** set your own secret key in `bootloader/src/Password.h`
> (`SPECK_KEY`, shared automatically with the Python toolchain), and **re-generate
> `application.fw`** — the `.fw` format changed and old files are incompatible.
> LTO and the 16-bit timer are validated in simulation only and should be confirmed
> on real hardware.

Full details: [`bootloader/src/criptography.md`](bootloader/src/criptography.md) and
[`bootloader/docs/analisi-memoria.md`](bootloader/docs/analisi-memoria.md).

## What this project does

The goal of this repository is to provide a practical, end-to-end custom firmware update path for an AVR board:

- build a custom bootloader,
- install it on the target device,
- compile an application image,
- package it for secure update,
- and send it to the board through the bootloader protocol.

The design includes:

- USB bootloader support for ATmega32U4,
- a simple command protocol between PC and bootloader,
- encrypted firmware payload handling,
- a small GUI for updating firmware from a desktop environment.

---

## Project structure

- `bootloader/`  
  Source code and build files for the USB bootloader.

- `application/`  
  Example application sketch used as the user firmware.

- `toolchain/`  
  Python automation scripts for building, installing, and flashing the bootloader/application.

- `firmware-updater/`  
  GUI-based firmware updater application built with PyWebView.

- `docs/`  
  Notes and reference material for the protocol and implementation details.

---

## Main workflow

1. Compile the bootloader.
2. Install the programmer support on the board.
3. Flash the custom bootloader to the target device.
4. Compile the application firmware.
5. Convert the application into the firmware format expected by the bootloader.
6. Use the updater tool to send the encrypted firmware image to the board.

This makes the project useful both as a learning tool and as a starting point for custom AVR firmware update pipelines.

---

## Hardware and software requirements

### Hardware

- An ATmega32U4-based board (Leonardo/Micro class)
- USB connection for programming and update operations
- A compatible AVR programmer/programming interface for initial bootloader installation

### Software

- Python 3
- Arduino CLI (used for application compilation)
- AVR-GCC / AVR toolchain
- avrdude
- PyWebView for the GUI updater

---

## How to use the toolchain

The Python entry point under `toolchain/` is the main automation interface.

Typical operations include:

- compile the bootloader,
- compile the application,
- select a COM port,
- install the programmer,
- install the bootloader,
- load an application image,
- read memory.

The actual command entry point is the script:

- `toolchain/main.py`

---

## Firmware updater

The updater under `firmware-updater/` provides a desktop GUI that:

- opens a firmware file,
- lists available serial ports,
- starts the update process,
- and reports progress/status back to the user.

This is the user-facing update flow for the custom bootloader.

---

## Notes

- The firmware update path encrypts memory-write payloads with Speck 32/64 in CTR
  mode (see "Changes in this fork" above). Note that encryption provides
  confidentiality only, not authenticity — a signature/MAC would be needed for a
  fully secure update path.
- The bootloader protocol is intentionally simple and designed for controlled firmware updates.
- This repository is still a development project, so some parts may be incomplete or experimental depending on the current branch state.

---

## Summary

This repository combines:

- custom AVR bootloader firmware,
- a build and flashing toolchain,
- and a GUI-based updater.

Together, these pieces form a small but complete ecosystem for custom AVR firmware deployment.
