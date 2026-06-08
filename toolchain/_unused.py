import subprocess

def help(exe_name: str):
    subprocess.run([
        exe_name, "--help"
    ])


def selective_upload(selected_com: str, file_name: str):
    print(f"loading {file_name}")
    subprocess.run([
        AVRDUDE,
        "-c", "arduino_as_isp",
        "-P", selected_com,
        "-p", "m32u4",
        "-D", # disable auto erase
        "-U", f"flash:w:{WORKSPACE_FOLDER}/dist/{file_name}.elf:e",
    ])

def assembly_from_hex(file_name):
    print(f"converting from hex to assembly for {file_name}")
    with open(f"{WORKSPACE_FOLDER}/dist/{file_name}.asm", "w", encoding="utf-8") as output_file:
        subprocess.run(
            [
                AVR_OBJDUMP,
                "--source",
                "--disassemble-all",
                "--target=ihex",
                "--architecture=avr:105",
                f"{WORKSPACE_FOLDER}/dist/{file_name}.hex", # percorso file sorgente
            ],
            stdout=output_file,
            stderr=subprocess.PIPE,
            text=True
        )

def bin_from_elf(file_name: str):
    print(f"converting from elf to binary for {file_name}")
    subprocess.run([
        AVR_OBJCOPY,
        "-O", "binary",
        f"{WORKSPACE_FOLDER}/dist/{file_name}.elf", # percorso file sorgente
        f"{WORKSPACE_FOLDER}/dist/{file_name}.bin", # percorso file convertito
    ])

def hex_from_elf(file_name: str):
    print(f"converting from elf to hex for {file_name}")
    subprocess.run([
        AVR_OBJCOPY,
        "-O", "ihex",
        f"{WORKSPACE_FOLDER}/dist/{file_name}.elf", # percorso file sorgente
        f"{WORKSPACE_FOLDER}/dist/{file_name}.hex", # percorso file convertito
    ])

def hex_from_bin(file_name: str):
    print(f"converting from binary to hex for {file_name}")
    subprocess.run([
        AVR_OBJCOPY,
        "-I", "binary",
        "-O", "ihex",
        f"{WORKSPACE_FOLDER}/dist/{file_name}.bin", # percorso file sorgente
        f"{WORKSPACE_FOLDER}/dist/{file_name}.hex", # percorso file convertito
    ])

def bin_from_hex(file_name: str):
    print(f"converting from hex to binary for {file_name}")
    subprocess.run([
        AVR_OBJCOPY,
        "-O", "binary",
        "-I", "ihex",
        f"{WORKSPACE_FOLDER}/dist/{file_name}.hex", # percorso file sorgente
        f"{WORKSPACE_FOLDER}/dist/{file_name}.bin", # percorso file convertito
    ])

def text_from_bin(file_name: str):
    print(f"converting from binary to text for {file_name}")
    with open(f"{WORKSPACE_FOLDER}/dist/{file_name}.bin", "rb") as bin_file:
        data = bin_file.read()
    hex_values = [f"0x{byte:02X}" for byte in data]
    lines = [", ".join(hex_values[i:i+16]) for i in range(0, len(hex_values), 16)]
    hex_string = "\n".join(lines)
    text_file_name = f"{WORKSPACE_FOLDER}/dist/{file_name}.txt"
    with open(text_file_name, "w") as text_file:
        text_file.write(hex_string)
    print(f"Hex values written to {text_file_name}")


def elf_from_hex(file_name: str):
    print(f"converting from hex to elf for {file_name}")
    subprocess.run([
        AVR_OBJCOPY,
        "-I", "ihex",
        "-O", "elf32-avr",
        f"{WORKSPACE_FOLDER}/dist/{file_name}.hex", # percorso file sorgente
        f"{WORKSPACE_FOLDER}/dist/{file_name}.elf", # percorso file convertito
    ])

def download(selected_com: str, file_name: str):
    print(f"downloading memory to file {file_name}")
    subprocess.run([
        AVRDUDE,
        "-c", "arduino_as_isp",
        "-P", selected_com,
        "-p", "m32u4",
        "-U", f"flash:r:{WORKSPACE_FOLDER}/dist/{file_name}.hex:i",
    ])


# file_name: il nome del file .c da compilare (e corrispondente nome dell'elf compilato)
# start_address: l'indirizzo di memoria da cui deve partire il programma (es '0x3800')
def compile(file_name: str, start_address: str = None):
    print(f"compiling {file_name} at address {start_address}")
    command_line = [
        AVR_GCC,
        "-Wall", # warnings
        "-Os", # optimize for size
        "-mmcu=atmega32u4", # target
    ]
    if start_address:
        command_line.append(
            f"-Wl,-section-start=.text={start_address}",
        )
    command_line.extend([
        "-std=gnu99", # standard C99 (penso...)
        "-o", f"{WORKSPACE_FOLDER}/dist/{file_name}.elf", # percorso output compilato
        f"{WORKSPACE_FOLDER}/{file_name}.c", # percorso file sorgente
    ])
    subprocess.run(command_line)

def read_configuration(selected_com):
    print('reading configuration')
    subprocess.run([
        AVRDUDE,
        "-c", "arduino_as_isp",
        "-P", selected_com,
        "-p", "m32u4",
        "-U", "lfuse:r:-:i",
        "-U", "hfuse:r:-:i",
        "-U", "efuse:r:-:i",
        "-U", "lock:r:-:i",
    ])