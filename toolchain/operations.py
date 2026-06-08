import os
import shutil
import subprocess
import inspect
import bootloader_handler as bootloader

def log_function_call():
    frame = inspect.currentframe().f_back
    function_name = frame.f_code.co_name
    args = ", ".join(f"{k}={v!r}" for k, v in frame.f_locals.items())
    print(f"{function_name}({args})")

# ------------------------------------------------------------------------------

# workspace
WORKSPACE_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# folders
BOOTLOADER =  os.path.join(WORKSPACE_FOLDER, 'bootloader')
APPLICATION =  os.path.join(WORKSPACE_FOLDER, 'application')
DEVICE =  os.path.join(WORKSPACE_FOLDER, 'device')

# tools
ARDUINO_CLI = os.path.join(WORKSPACE_FOLDER, 'toolchain', 'arduino-cli', 'arduino-cli.exe')
AVRDUDE = os.path.join(WORKSPACE_FOLDER, 'toolchain', 'avrdude', 'avrdude.exe')
AVR_GCC = os.path.join(WORKSPACE_FOLDER, 'toolchain', 'avr8-gnu-toolchain-win32_x86_64', 'bin', 'avr-gcc.exe')
AVR_OBJCOPY = os.path.join(WORKSPACE_FOLDER, 'toolchain', 'avr8-gnu-toolchain-win32_x86_64', 'bin', 'avr-objcopy.exe')
AVR_OBJDUMP = os.path.join(WORKSPACE_FOLDER, 'toolchain', 'avr8-gnu-toolchain-win32_x86_64', 'bin', 'avr-objdump.exe')

# ------------------------------------------------------------------------------

def reset_board(selected_com):
    log_function_call()
    subprocess.run([
        AVRDUDE,
        "-c", "arduino_as_isp",
        "-P", selected_com,
        "-p", "m32u4",
        "-e",
        "-U", "lfuse:w:0xFF:m",
        "-U", "hfuse:w:0xD8:m",
        "-U", "efuse:w:0xCB:m",
        "-U", "lock:w:0xFF:m",
    ])

def lock_memory_read(selected_com):
    log_function_call()
    subprocess.run([
        AVRDUDE,
        "-c", "arduino_as_isp",
        "-P", selected_com,
        "-p", "m32u4",
        # LPM boot, LPM application = disabled.
        # SPM boot, SPM application = enabled.
        "-U", "lock:w:0xCC:m",
    ])

def install_bootloader(selected_com):
    log_function_call()
    reset_board(selected_com)
    bootlooader_path = os.path.join(BOOTLOADER, 'dist', 'Caterina.hex')
    upload(selected_com, bootlooader_path)



def load_application(selected_com):
    log_function_call()
    bootloader.setup(selected_com)

    # reset request

    bootloader.request_reset()
    
    # memory write
    
    fw_file_path = os.path.join(APPLICATION, 'dist', 'application.fw')
    packets = bootloader.unpack_fw_file(fw_file_path)
    count = 0
    for packet in packets:
        count += 1;

        request: bootloader.Request = bootloader.Request()
        request.identifier = count
        request.command = bootloader.Command.WRITE_MEMORY_PAGE
        request.payload = bootloader.decrypt(list(packet))
        request.payload_length = len(request.payload)

        bootloader.send(request)

        response: bootloader.Response = bootloader.receive(decrypt_payload=True)

        if response.status != bootloader.Status.PROCESSED:
            raise Exception(f'bootloader did not process the message number {count}')
    
    # application enable
    
    request: bootloader.Request = bootloader.Request()
    request.identifier = count
    count += 1
    request.command = bootloader.Command.APPLICATION_ENABLE
    request.payload = []
    request.payload_length = 0
    bootloader.send(request)

    response: bootloader.Response = bootloader.receive(decrypt_payload=False)

    if response.status != bootloader.Status.PROCESSED:
        raise Exception(f'bootloader did not process the application enable message (number {count})')
    
    # start sketch

    request: bootloader.Request = bootloader.Request()
    request.identifier = count
    request.command = bootloader.Command.START_SKETCH
    request.payload = []
    request.payload_length = 0
    bootloader.send(request)

    response: bootloader.Response = bootloader.receive(decrypt_payload=False)

    if response.status != bootloader.Status.PROCESSED:
        raise Exception(f'bootloader did not process the start sketch message (number {count})')

    # end
    
    bootloader.teardown()



def install_programmer(selected_com, old_bootloader=False):
    log_function_call()
    command_line = [
        AVRDUDE,
        "-c", "arduino",
        "-P", selected_com,
        "-p", "atmega328p",
    ]

    if old_bootloader:
        command_line.extend([
            "-b", "57600", # bootloader pre 2018
        ])
    else:
        command_line.extend([
            "-b", "115200", # bootloader post 2018
        ])

    command_line.extend([
        "-U", f"flash:w:{WORKSPACE_FOLDER}/toolchain/programmer_firmware/dist/programmer_firmware.ino.hex:i",
    ])

    subprocess.run(command_line)
    

def read_memory(selected_com):
    file_output = os.path.join(DEVICE, 'memory.hex')
    subprocess.run([
        AVRDUDE,
        "-c", "arduino_as_isp",
        "-P", selected_com,
        "-p", "m32u4",
        "-U", f"flash:r:{file_output}:i",
    ])


def compile_bootloader():
    dist = os.path.join(BOOTLOADER, 'dist')
    clean_folder(dist)
    os.chdir(BOOTLOADER)
    subprocess.run(['make', 'clean'])
    subprocess.run(['make'])
    shutil.move('Caterina.hex', dist)
    subprocess.run(['make', 'clean'])


def compile_application():
    log_function_call()
    application = os.path.join(APPLICATION, 'application.ino')
    build = os.path.join(APPLICATION, 'build')
    clean_folder(build)
    dist = os.path.join(APPLICATION, 'dist')
    clean_folder(dist)
    output = os.path.join(build, 'application.ino.hex')
    subprocess.run([
        ARDUINO_CLI, 'compile',
        '--fqbn', 'arduino:avr:leonardo',
        '--build-path', build,
        application
        ])
    shutil.move(output, dist)
    delete_folder(build)
    hex_file = os.path.join(dist, 'application.ino.hex')
    data: list[bootloader.MemoryPage] = bootloader.extract_data_from_hex(hex_file)
    fw_file = os.path.join(dist, 'application.fw')
    bootloader.write_fw_file(fw_file, data)



def upload(selected_com, file):
    log_function_call()
    extension = file.split('.')[-1]
    mode = ''
    if 'elf' == extension:
        mode = 'e'
    elif 'hex' == extension:
        mode = 'i'
    else:
        raise('unknonwn file extension')
    subprocess.run([
        AVRDUDE,
        "-c", "arduino_as_isp",
        "-P", selected_com,
        "-p", "m32u4",
        "-U", f"flash:w:{file}:{mode}",
    ])



# ------------------------------------------------------------------------------

def delete_folder(path):
    log_function_call()
    not_ok = True
    while (not_ok):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            not_ok = False
        except:
            not_ok = True

def clean_folder(path):
    delete_folder(path)
    os.makedirs(path)