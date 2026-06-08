# Communication Protocol - Bootloader

## Message Structure

A message between devices (PC and bootloader) has the following structure:

- **Start byte (1 byte)**: Indicates the start of the message (fixed value `0x55`).
- **Identifier (1 byte)**: Identifies the transaction. The value is chosen by the PC and reused by the bootloader to refer to the response to a specific message.
- **Command (1 byte)**: Specifies the requested command (for example, bootloader version, memory write, etc.).
- **Payload Length (1 byte)**: Length of the payload data.
- **Payload (N bytes)**: Command-specific data.
- **CRC (1 byte)**: Verifies the integrity of the message.

## Protocol Phases

1. **Message Reception**:
   - The device receives a message containing the command, data, and CRC.
   - The integrity of the message is verified with the CRC.

2. **Command Execution**:
   - If the message is valid, the device executes the command specified in the message.
   - Example commands: "Bootloader Version", "Keep Alive", "Memory Write", "Start Sketch".

3. **Response Generation**:
   - The device generates a response that includes:
     - Operation status (success or error).
     - Data (if applicable) and CRC.

4. **Response Transmission**:
   - The response is transmitted with the same structure as the request message, including a CRC.

## Commands and Responses

1. **CMD_BOOTLOADER_VERSION** (`0x00`)
   - **Description**: Request for the bootloader version.
   - **Response Message**:
     - **Status**: `CP_PROCESSED`
     - **Response**: Bootloader version
     - **Payload**: `[major version, minor version, hardware major, hardware minor]` (4 bytes)

2. **CMD_KEEP_ALIVE** (`0x01`)
   - **Description**: A keep-alive command to keep the bootloader active.
   - **Response Message**:
     - **Status**: `CP_PROCESSED`
     - **Response**: No data (0 payload bytes).

3. **CMD_WRITE_MEMORY_PAGE** (`0x02`)
   - **Description**: Writing one flash memory page.
   - **Response Message**:
     - **Status**: `CP_PROCESSED`, `CP_FLASH_ADDRESS_NOT_ALIGNED`, `CP_FLASH_ADDRESS_OUT_OF_BOUNDS`
     - **Response**: Written flash page address
     - **Payload**: `[page address (2 bytes)]` (after encryption)

4. **CMD_START_SKETCH** (`0x03`)
   - **Description**: Start the main application (sketch).
   - **Response Message**:
     - **Status**: `CP_PROCESSED`
     - **Response**: No data (0 payload bytes).

## Command Details

### **CMD_BOOTLOADER_VERSION**
- **Description**: The device requests the version of the bootloader and hardware.
- **Behavior**:
  - The response includes:
    - Bootloader version (2 bytes: major, minor).
    - Hardware version (2 bytes: major, minor).
- **Command Code**: `0x00`
- **Response Payload**: `[major_version, minor_version, hw_major, hw_minor]` (4 bytes).

### **CMD_KEEP_ALIVE**
- **Description**: Keeps the bootloader active and prevents it from entering timeout mode.
- **Behavior**:
  - The response is a success message with no additional data.
- **Command Code**: `0x01`
- **Response Payload**: No data.

### **CMD_WRITE_MEMORY_PAGE**
- **Description**: Writes a flash memory page at a specified address. The data is decrypted before writing and encrypted before sending the response.
- **Behavior**:
  - If the address is not correctly aligned or is out of the bootloader memory bounds, the response contains an error:
    - `CP_FLASH_ADDRESS_NOT_ALIGNED`: The page address is not aligned to the page size.
    - `CP_FLASH_ADDRESS_OUT_OF_BOUNDS`: The page address is outside the valid range.
  - If the command succeeds, the response contains the written page address.
- **Command Code**: `0x02`
- **Response Payload**: `[page_address (2 bytes)]` (after encryption).

### **CMD_START_SKETCH**
- **Description**: Starts the main application (sketch) and disables the bootloader.
- **Behavior**:
  - The response is a success message with no additional data.
- **Command Code**: `0x03`
- **Response Payload**: No data.

## Response Structure for Each Command

The response for each command follows this structure:

1. **Start byte**: `0x55`
2. **Identifier**: Transaction identifier (chosen by the PC).
3. **Status**: Indicates whether the operation completed successfully or resulted in an error.
4. **Payload Length**: The length of the payload data in the response.
5. **Payload**: The response-specific data (for example, versions, memory address).
6. **CRC**: A CRC check to verify the integrity of the response.

## Example Communication Flow

1. **Request from device A to B**:
   - Command: `CMD_BOOTLOADER_VERSION`
   - Command Code: `0`
   - Message: `0x55 | Identifier_1 | 0 | 0 | CRC`

2. **Response from device B to A**:
   - Status: `CP_PROCESSED`
   - Message: `0x55 | Identifier_1 | CP_PROCESSED | 4 | [1, 2, 3, 4] | CRC` (Version 1.2, Hardware 3.4)

3. **Request from device A to B**:
   - Command: `CMD_WRITE_MEMORY_PAGE`
   - Command Code: `0x02`
   - Message: `0x55 | Identifier_2 | 2 | [payload data] | CRC`

4. **Response from device B to A**:
   - Status: `CP_PROCESSED`
   - Message: `0x55 | Identifier_2 | CP_PROCESSED | 2 | [0x00, 0x01] | CRC` (Written page address)
