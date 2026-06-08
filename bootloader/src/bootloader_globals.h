#ifndef BOOTLOADER_GLOBALS_H
#define BOOTLOADER_GLOBALS_H

#include <stdint.h>
#define BOOTLOADER_TIMEOUT 60000 // ms

/** Version major of the CDC bootloader. */
#define BOOTLOADER_VERSION_MAJOR 0x01

/** Version minor of the CDC bootloader. */
#define BOOTLOADER_VERSION_MINOR 0x00

/** Hardware version major of the CDC bootloader. */
#define BOOTLOADER_HWVERSION_MAJOR 0x01

/** Hardware version minor of the CDC bootloader. */
#define BOOTLOADER_HWVERSION_MINOR 0x00

#define FLASH_PAGE_SIZE (64 * 2)
#define FLASH_ADDRESS_SIZE 2
#define FLASH_BOOTLOADER_ADDRESS 0x7000

#endif // BOOTLOADER_GLOBALS_H