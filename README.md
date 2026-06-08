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

- The firmware update path uses encrypted payload handling for memory writes.
- The bootloader protocol is intentionally simple and designed for controlled firmware updates.
- This repository is still a development project, so some parts may be incomplete or experimental depending on the current branch state.

---

## Summary

This repository combines:

- custom AVR bootloader firmware,
- a build and flashing toolchain,
- and a GUI-based updater.

Together, these pieces form a small but complete ecosystem for custom AVR firmware deployment.
