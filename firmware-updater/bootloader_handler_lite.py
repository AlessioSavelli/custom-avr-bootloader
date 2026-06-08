import serial
import os
import time

from enum import IntEnum

from dataclasses import dataclass

# workspace
WORKSPACE_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))



# ------------------------------------------------------------------------------

START_BYTE = 0x55
POLYNOMIAL = [0x37]

class Command(IntEnum):
    BOOTLOADER_VERSION = 0x00
    KEEP_ALIVE = 0x01
    WRITE_MEMORY_PAGE = 0x02
    APPLICATION_ENABLE = 0x03
    START_SKETCH = 0xF0

    def __repr__(self) -> str:
        return f"<Command.{self.name}: {self.value}>"

class Status(IntEnum):
    NONE = 0
    RECEIVED = 1
    PROCESSED = 2
    DELIVERED = 3
    APPLICATION_DETECTED = 4

    MISSING_MESSAGE_STRUCT = 0x20
    MISSING_RX_FUNCTION = 0x21
    MISSING_TX_FUNCTION = 0x22
    NO_PROCESS_FUNCTION = 0x23
    ANSWER_TOO_LONG = 0x24

    WRONG_START = 0x40
    WRONG_LENGTH = 0x41
    WRONG_CRC = 0x42
    UNKNOWN_COMMAND = 0x43

    FLASH_ADDRESS_NOT_ALIGNED = 0x60
    FLASH_ADDRESS_OUT_OF_BOUNDS = 0x61

    def __repr__(self) -> str:
        return f"<Status.{self.name}: {self.value}>"

@dataclass
class Request:
    identifier: int
    command: Command
    payload_length: int
    payload: list[int]

    def bufferize(self) -> bytearray:
        buffer = [START_BYTE, self.identifier, self.command, self.payload_length]
        buffer.extend(self.payload)
        buffer.append(crc8(buffer[1:]))
        return bytearray(buffer)

class Response:
    identifier: int
    status: Status
    payload_length: int
    payload: list[int]
    crc: int

    def __repr__(self) -> str:
        output = 'Response:\n'
        output += f'  identifier: {self.identifier}\n'
        output += f'  status: {repr(self.status)}\n'
        output += f'  payload_length: {self.payload_length}\n'
        output += f'  payload: {self.payload}\n'
        return output
    
    def crc_wrong(self) -> bool:
        buffer = [self.identifier, self.status, self.payload_length]
        buffer.extend(self.payload)
        return crc8(buffer) != self.crc
    
    def simple_check(self) -> None:
        if self.status != Status.PROCESSED:
            raise Exception(f'Error: staus = {self.status}')




def setup(selected_com):
    global serial_port
    serial_port = serial.Serial(selected_com, baudrate=115200, timeout=1.0)
    return serial_port

def teardown():
    global serial_port
    serial_port.close()

def request_reset():
    serial_port.write(b'{RST}')

def send(request: Request) -> None:
    global serial_port
    print(f'sending {request}')
    serial_port.write(request.bufferize())

def receive_bytes(length: int) -> list[int]:
    data = []
    start = time.time()
    while time.time() - start < 5.0:
        data.extend(list(serial_port.read()))
        if len(data) >= length:
            return data
    return data

def receive() -> Response:
    global serial_port

    start = receive_bytes(1)[0]
    if start != START_BYTE:
        serial_port.reset_input_buffer()
        raise Exception('start not detected')
    
    input = Response()
    input.identifier = receive_bytes(1)[0]
    input.status = Status(receive_bytes(1)[0])
    input.payload_length = receive_bytes(1)[0]
    
    input.payload = []
    if input.payload_length > 0:
        input.payload = list(receive_bytes(input.payload_length))

    input.crc = receive_bytes(1)[0]

    if input.crc_wrong():
        serial_port.reset_input_buffer()
        raise Exception('crc wrong')
    
    print(f'received {input}')
    return input

# ------------------------------------------------------------------------------

def crc8(buffer: list[int]) -> int:
    global POLYNOMIAL
    crc = 0
    for byte in buffer:
        crc ^= byte
        for _ in reversed(range(8)):
            feedback_bit = crc & 0x80
            crc <<= 1
            crc &= 0xFF
            if 0 != feedback_bit:
                crc ^= POLYNOMIAL[0]
    return crc

# ------------------------------------------------------------------------------

def unpack_fw_file(fw_path: str) -> list[bytes]:
    with open(fw_path, 'rb') as fw_file:
        data = fw_file.read()
    
    packets = []
    packet_size = 130
    i = 0
    while i < len(data):
        packets.append(data[i:i+packet_size])
        i += packet_size
    
    return packets