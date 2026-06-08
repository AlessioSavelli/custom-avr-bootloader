import sys
import time
import serial
from intelhex import IntelHex

FLASH_PAGE_SIZE = 128  # puoi cambiare a 256 se serve

def open_serial(port, baudrate=57600, timeout=1.0):
    return serial.Serial(port, baudrate, timeout=timeout)

def send_cmd(ser, cmd):
    ser.write(cmd.encode('ascii'))
    return ser.read_until(b'\r')

def send_bin(ser, data):
    ser.write(data)
    return ser.read_until(b'\r')

def parse_hex_file(hex_path):
    ih = IntelHex(hex_path)
    data = {}
    for addr in range(ih.minaddr(), ih.maxaddr() + 1):
        data[addr] = ih[addr]
    return data

def align_and_chunk(data, chunk_size):
    if not data:
        return []
    start = min(data.keys())
    end = max(data.keys())
    chunks = []
    for base in range(start, end + 1, chunk_size):
        chunk = [data.get(addr, 0xFF) for addr in range(base, base + chunk_size)]
        chunks.append((base, chunk))
    return chunks

def enter_bootloader_prompt(port):
    print(f"[INFO] Waiting for device {port} to appear...")
    while True:
        try:
            return open_serial(port)
        except Exception:
            time.sleep(0.1)

def upload_hex(port, hex_path):
    ser = enter_bootloader_prompt(port)
    print("[INFO] Connected to serial port.")

    # Sync
    idn = send_cmd(ser, 'S\r')
    print(f"[INFO] Bootloader ID: {idn.strip().decode(errors='ignore')}")
    send_cmd(ser, 'V\r')  # version

    # Erase
    print("[INFO] Erasing flash...")
    send_cmd(ser, 'e\r')

    # Parse hex
    raw_data = parse_hex_file(hex_path)
    chunks = align_and_chunk(raw_data, FLASH_PAGE_SIZE)

    # Upload
    for base_addr, chunk in chunks:
        word_addr = base_addr // 2
        ah = (word_addr >> 8) & 0xFF
        al = word_addr & 0xFF

        send_bin(ser, bytes([ord('A'), ah, al]))  # Set address
        resp = ser.read_until(b'\r')
        if resp != b'\r':
            print(f"[ERROR] Set address failed at {hex(base_addr)}")
            break

        length = len(chunk)
        lh = (length >> 8) & 0xFF
        ll = length & 0xFF
        send_bin(ser, bytes([ord('B'), lh, ll, ord('F')]) + bytes(chunk))
        resp = ser.read_until(b'\r')
        if resp != b'\r':
            print(f"[ERROR] Write failed at {hex(base_addr)}")
            break

        print(f"[INFO] Wrote {length} bytes at {hex(base_addr)}")

    # Jump to user code
    print("[INFO] Jumping to application...")
    send_cmd(ser, 'E\r')

    ser.close()
    print("[DONE] Upload completed.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python caterina_uploader.py <serial_port> <file.hex>")
        sys.exit(1)

    port = sys.argv[1]
    hex_path = sys.argv[2]
    upload_hex(port, hex_path)
