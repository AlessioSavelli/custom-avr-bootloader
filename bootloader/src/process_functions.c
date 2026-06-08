#include <avr/boot.h>

#include "command_processor.h"
#include "process_functions.h"
#include "bootloader_globals.h"
#include "Criptography.h"
#include "bootloader_timer.h"

static CP_status_t ok_response(message_s *message)
{
    return message->status = CP_PROCESSED;
}

CP_status_t PF_bootloader_version(message_s *message)
{
    message->answer_payload[BOOTLOADER_VERSION_MAJOR] = 0;
    message->answer_payload[BOOTLOADER_VERSION_MINOR] = 0;
    message->answer_payload[BOOTLOADER_HWVERSION_MAJOR] = 0;
    message->answer_payload[BOOTLOADER_HWVERSION_MINOR] = 0;
    message->answer_payload_length = 4;
    return ok_response(message);
}

CP_status_t PF_keep_alive(message_s *message)
{
    BT_timer_start(&bootloader_timer);
    message->answer_payload_length = 0;
    return ok_response(message);
}

CP_status_t PF_application_enable(message_s *message)
{
    boot_rww_enable_safe();
    message->answer_payload_length = 0;
    return ok_response(message);
}

CP_status_t PF_write_memory_page(message_s *message)
{
    CRI_decrypt(message->payload, message->payload_length);

    uint16_t page_address = message->payload[0];
    page_address <<= 8;
    page_address += message->payload[1];

    // prepare answer that contains FLASH address in any case
    message->answer_payload_length = 2;
    message->answer_payload[0] = page_address >> 8;
    message->answer_payload[1] = page_address >> 0;
    CRI_encrypt(message->answer_payload, message->answer_payload_length);

    if (0 != (page_address % FLASH_PAGE_SIZE))
    {
        return message->status = CP_FLASH_ADDRESS_NOT_ALIGNED;
    }

    if (page_address >= FLASH_BOOTLOADER_ADDRESS)
    {
        return message->status = CP_FLASH_ADDRESS_OUT_OF_BOUNDS;
    }

    // security check passed
    // proceed to write flash page

    boot_page_erase(page_address);
    boot_spm_busy_wait();

    for (uint8_t i = 0; i < FLASH_PAGE_SIZE; i += 2)
    {
        uint16_t word = message->payload[2 + i + 1];
        word <<= 8;
        word += message->payload[2 + i];
        boot_page_fill(page_address + i, word);
    }

    boot_page_write(page_address);
    boot_spm_busy_wait();

    return ok_response(message);
}

CP_status_t PF_start_sketch(message_s *message)
{
    BT_timer_start(&bootloader_timer);
    bootloader_timer -= BOOTLOADER_TIMEOUT - 100;
    message->answer_payload_length = 0;
    return ok_response(message);
}
