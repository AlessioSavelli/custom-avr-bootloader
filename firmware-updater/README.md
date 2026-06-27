# Firmware updater

## Requirements

- The user can update a board equipped with a custom AVR bootloader.
- The user must have:
  - A USB connection (virtual serial port) to the board.
  - An encrypted .fw file.
- The user and the software must not be able to decrypt the contents of the .fw file.
- The procedure must be strict and guided to limit variability and errors.
- Basic logging to diagnose any issues afterward.
- The ability to distinguish 2 or more connected boards.

## Detailed design

- The software has a frontend and a backend, built with the PyWebView system.
- The frontend manages the steps the user must follow:
  1. Load a .fw file.
  2. Select a serial port.
  3. Firmware update with a progress bar.
  4. Start the application or report any errors.
- The backend handles communication with the board over USB.
- Backend and frontend communicate through a text protocol:
  - message type
  - message content

### Protocol

> F = Frontend  
> B = Backend  

Messages:
- F -> B: Load file.
  - B -> F: Response with the file path.
- F -> B: Request COM port list.
  - B -> F: Response with the COM port list.
- F -> B: Request to start an update (file, port).
  - B -> F: Acknowledgement of receipt.
- B -> F: Update status:
  - in progress (% complete)
  - finished (possible errors)

## Note on encryption

The `.fw` file is encrypted with **Speck 32/64 in CTR mode** (the toolchain and the
bootloader share the same secret key). The updater only relays the already-encrypted
pages to the board, so neither the user nor this GUI needs — or is able — to decrypt
the firmware contents. See [`../bootloader/src/criptography.md`](../bootloader/src/criptography.md).