# ✅ Progress & to-dos

> Legend: `[x]` done · `[~]` partly done / to be tested · `[ ]` to do

---

## 🎯 Goals

- [x] Compile the bootloader with `make`
- [x] Compile the application with `arduino-cli`
- [x] Select the COM port
- [x] Install the programmer on the Nano
- [x] Install the bootloader on the Olimex board through the Nano
- [x] Upload the application firmware through the bootloader
- [x] Verify that downloading (reading back) the firmware is not possible

## 🔧 Bootloader

- [x] USB communication
- [x] Command parser
- [x] Content decryption
- [x] Writing to application memory
- [x] Application startup

## 🧱 Application

- [ ] Bootloader access request handling

## 🐍 Toolchain

- [x] Bootloader compilation
- [x] Application compilation
- [x] Generation of encrypted application firmware (`.fw`)
- [x] Device reset
- [x] Bootloader installation
- [x] Memory-read blocking
- [x] Transfer of `.fw` to the board

## 🖥️ Client software

- [x] User GUI
- [x] Bootloader request
- [x] Transfer of `.fw` to the board

## 🔐 Security & size hardening (this fork)

- [x] Replace repeating-key XOR with **Speck 32/64-CTR** (real block cipher, 64-bit key)
- [x] Per-page nonce (page address) → no keystream reuse, no identical-page leak
- [x] Cross-validation: official Speck test vector + C/Python + `avr-gdb` simulator
- [x] Keep the robust cipher within the 4 KB boot section (**4076 → 4088 B**)
- [x] Size/RAM optimizations: LTO, on-the-fly key schedule, 16-bit timer, 8 B key (RAM `.data+.bss` **308 → 174 B**)
- [~] Validate LTO + 16-bit timer on **real hardware** (simulated only so far)
- [ ] Authenticity (signature/MAC) — currently confidentiality only
- [ ] Optional: rewrite the Speck core in AVR assembly for more flash headroom
