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

