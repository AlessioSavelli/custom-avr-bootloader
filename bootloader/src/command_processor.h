#ifndef CMD_PROCESSOR_H
#define CMD_PROCESSOR_H

#include <stdint.h>

enum
{
    CP_NONE = 0x00,
    CP_RECEIVED = 0x01,
    CP_PROCESSED = 0x02,
    CP_DELIVERED = 0x03,
    CP_APPLICATION_DETECTED = 0x04,

    // programming errors
    CP_MISSING_MESSAGE_STRUCT = 0x20,
    CP_MISSING_RX_FUNCTION = 0x21,
    CP_MISSING_TX_FUNCTION = 0x22,
    CP_NO_PROCESS_FUNCTION = 0x23,
    CP_ANSWER_TOO_LONG = 0x24,

    // protocol errors
    CP_WRONG_START = 0x40,
    CP_WRONG_LENGTH = 0x41,
    CP_WRONG_CRC = 0x42,
    CP_UNKNOWN_COMMAND = 0x43,

    // specific command errors
    CP_FLASH_ADDRESS_NOT_ALIGNED = 0x60,
    CP_FLASH_ADDRESS_OUT_OF_BOUNDS = 0x61,
};
typedef uint16_t CP_status_t;

enum
{
    CP_BOOTLOADER_VERSION = 0x00,
    CP_KEEP_ALIVE = 0x01,
    CP_WRITE_MEMORY_PAGE = 0x02,
    CP_APPLICATION_ENABLE = 0x03,

    CP_START_SKETCH = 0xF0,
};
typedef uint8_t CP_command_t;

#define MAX_PAYLOAD_LENGTH (2 + (64 * 2))

typedef struct message_s
{
    uint8_t start;
    uint8_t identifier;
    CP_command_t command;
    uint8_t payload_length;
    uint8_t payload[MAX_PAYLOAD_LENGTH];
    uint8_t crc;
    uint8_t answer_payload_length;
    uint8_t answer_payload[MAX_PAYLOAD_LENGTH];
    CP_status_t status;
} message_s;

CP_status_t CMDP_main(void);

// -----------------------------------------------------------------------------

typedef void tx_function_t(uint8_t);
typedef uint8_t rx_function_t(void);

void CMDP_tx_point_set(tx_function_t *function_pointer);
void CMDP_rx_point_set(rx_function_t *function_pointer);


#endif // CMD_PROCESSOR_H