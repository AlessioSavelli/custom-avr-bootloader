# 🔌 Custom AVR Bootloader

> A complete, end-to-end workflow to **build, install, and securely update** custom firmware on an ATmega32U4 board (Arduino Leonardo / Micro class).

![MCU](https://img.shields.io/badge/MCU-ATmega32U4-1f6feb)
![Boot section](https://img.shields.io/badge/boot%20section-4%20KB-orange)
![Cipher](https://img.shields.io/badge/cipher-Speck%2032%2F64--CTR-2ea44f)
![USB](https://img.shields.io/badge/USB-CDC%20%C2%B7%20LUFA-8957e5)
![Toolchain](https://img.shields.io/badge/toolchain-Python%203-3776ab)

---

## 📑 Table of contents

- [✨ What this project does](#-what-this-project-does)
- [🔐 Changes in this fork (security & size)](#-changes-in-this-fork-security--size)
- [🗂️ Project structure](#-project-structure)
- [🔁 Main workflow](#-main-workflow)
- [🧰 Requirements](#-requirements)
- [⚙️ Using the toolchain](#-using-the-toolchain)
- [🖥️ Firmware updater](#-firmware-updater)
- [📝 Notes](#-notes)

---

## ✨ What this project does

The repository provides a practical, end-to-end custom firmware update path for an AVR board:

- 🏗️ build a custom bootloader,
- 📥 install it on the target device,
- 🧱 compile an application image,
- 📦 package it for a secure update,
- 🚀 and send it to the board through the bootloader protocol.

It is split into **three main parts**:

| Part | Folder | Role |
|------|--------|------|
| 🔧 **Bootloader firmware** | `bootloader/` | LUFA-based USB bootloader for the ATmega32U4: USB communication, command parsing, memory programming, application launch. |
| 🐍 **Toolchain** | `toolchain/` | Python scripts to compile, install the programmer, flash, package firmware, and pick the COM port — plus the low-level bootloader protocol. |
| 🖥️ **Firmware updater GUI** | `firmware-updater/` | A small PyWebView desktop app to load an encrypted firmware file and update the device. |

---

## 🔐 Changes in this fork (security & size)

This fork **hardens the firmware encryption** and reworks the bootloader so that a
**real block cipher fits in the same 4 KB boot section** that previously barely held a trivial one.

### 🛡️ Stronger encryption

| | Before | After |
|---|--------|-------|
| Scheme | repeating-key **XOR** | **Speck 32/64 in CTR mode** |
| Key | trivial `0x00, 0x01, … 0x7F` | **64-bit secret** key |
| Weaknesses | first byte in clear, no diffusion, identical pages → identical ciphertext | per-page **nonce** (page address) → no keystream reuse, no identical-page leak |

- ✅ **Validated three ways:** against the official **Speck32/64 test vector**, **byte-for-byte** between the C firmware and the Python toolchain, and by running the **AVR-compiled** cipher inside the `avr-gdb` simulator — all producing identical output.
- The page address now travels in clear (it *is* the public CTR nonce); only the 128 data bytes are encrypted.

### 📉 Memory footprint

> ATmega32U4 · the **4 KB boot section is a hard ceiling** (cannot be enlarged).

| Metric | Before (XOR) | After (Speck) |
|--------|-------------:|--------------:|
| Flash `Program` | 4076 B | **4088 B** |
| RAM (`.data + .bss`) | 308 B | **174 B** *(−43 %)* |
| Cipher strength | repeating-key XOR | real block cipher 🔒 |

The cipher itself grew (~304 B → ~416 B of code + key), but that cost was **paid back by size optimizations**, so the net flash change is only **+12 B**:

- 🔗 **LTO** (link-time optimization) enabled — *≈ −132 B*
- ⚡ Speck core shrunk **488 B → 408 B** (on-the-fly key schedule, shift-register instead of `l[i % 3]`, byte-swap rotations)
- ⏱️ bootloader **timer 32-bit → 16-bit** (the 60 s timeout fits in 16 bits) — *≈ −150 B* and most of the RAM saving
- 🔑 secret key shrunk **128 B → 8 B**

> ⚠️ **Before you deploy**
> - Set your **own** secret key in [`bootloader/src/Password.h`](bootloader/src/Password.h) (`SPECK_KEY`, shared automatically with the Python toolchain).
> - **Re-generate `application.fw`** — the `.fw` format changed, old files are incompatible.
> - LTO and the 16-bit timer are validated **in simulation only** → confirm on real hardware.

📖 Full details: [`bootloader/src/criptography.md`](bootloader/src/criptography.md) · [`bootloader/docs/memory-analysis.md`](bootloader/docs/memory-analysis.md)

---

## 🗂️ Project structure

```
custom-avr-bootloader/
├── bootloader/        🔧 USB bootloader firmware (C + LUFA) and build files
│   ├── src/              source + per-module docs (incl. criptography.md)
│   └── docs/             analysis notes (memory/size study)
├── application/       🧱 example application sketch (user firmware)
├── toolchain/         🐍 Python automation: build, install, flash, package
├── firmware-updater/  🖥️ PyWebView GUI updater
└── notes/             📝 protocol notes, to-dos, reference material
```

---

## 🔁 Main workflow

1. 🔨 Compile the bootloader.
2. 🔌 Install the programmer support on the board.
3. ⬇️ Flash the custom bootloader to the target device.
4. 🧱 Compile the application firmware.
5. 📦 Convert the application into the firmware format expected by the bootloader.
6. 🚀 Use the updater tool to send the encrypted firmware image to the board.

Useful both as a learning tool and as a starting point for custom AVR firmware update pipelines.

---

## 🧰 Requirements

**Hardware** 🛠️
- An ATmega32U4-based board (Leonardo / Micro class)
- USB connection for programming and update operations
- A compatible AVR programmer for the initial bootloader installation

**Software** 💾
- Python 3
- Arduino CLI (application compilation)
- AVR-GCC / AVR toolchain
- avrdude
- PyWebView (GUI updater)

---

## ⚙️ Using the toolchain

The Python entry point under `toolchain/` is the main automation interface
(`toolchain/main.py`). Typical operations:

- 🔨 compile the bootloader / application
- 🔌 select a COM port
- 📥 install the programmer / bootloader
- 🚀 load an application image
- 🔍 read memory

---

## 🖥️ Firmware updater

The updater under `firmware-updater/` provides a desktop GUI that:

- 📂 opens a firmware file,
- 🔌 lists available serial ports,
- ▶️ starts the update process,
- 📊 reports progress/status back to the user.

This is the user-facing update flow for the custom bootloader.

---

## 📝 Notes

- 🔐 Memory-write payloads are encrypted with **Speck 32/64 in CTR mode** (see [Changes in this fork](#-changes-in-this-fork-security--size)). Encryption provides **confidentiality only, not authenticity** — a signature/MAC would be needed for a fully secure update path.
- 🧩 The bootloader protocol is intentionally simple and designed for controlled firmware updates.
- 🚧 This is still a development project — some parts may be incomplete or experimental depending on the current branch state.

---

<sub>🔧 Custom AVR bootloader firmware · 🐍 build & flashing toolchain · 🖥️ GUI updater — a small but complete ecosystem for custom AVR firmware deployment.</sub>
