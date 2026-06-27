## Progress status

[x] = done
[~] = partly done / to be tested
[]  = not done / to do

## Goals

0. [x] compile the bootloader with make
1. [x] compile the application with arduino-cli
2. [x] select the COM port
3. [x] install the programmer on the Nano
4. [x] install the bootloader on the Olimex board through the Nano
5. [x] upload the application firmware through the bootloader
6. [x] verify that downloading the firmware is not possible


## Bootloader
- [x] USB communication
- [x] command parser
- [x] content decryption
- [x] writing to application memory
- [x] application startup

## Application
- [] bootloader access request handling

## Toolchain
- [x] bootloader compilation
- [x] application compilation
- [x] generation of encrypted application firmware (.fw)
- [x] device reset
- [x] bootloader installation
- [x] memory read blocking
- [x] transfer of .fw to the board

## Client software
- [x] user GUI
- [x] bootloader request
- [x] transfer of .fw to the board

## Security & size hardening (this fork)
- [x] replace repeating-key XOR with Speck 32/64-CTR (real block cipher, 64-bit key)
- [x] per-page nonce (page address) -> no keystream reuse, no identical-page leak
- [x] cross-validation: official Speck test vector + C/Python + avr-gdb simulator
- [x] keep the robust cipher within the 4 KB boot section (4076 -> 4088 B)
- [x] size/RAM optimizations: LTO, on-the-fly key schedule, 16-bit timer, 8 B key
      (RAM .data+.bss 308 -> 174 B)
- [~] validate LTO + 16-bit timer on real hardware (only simulated so far)
- [] authenticity (signature/MAC) - currently confidentiality only
- [] optional: rewrite Speck core in AVR assembly for more flash headroom

