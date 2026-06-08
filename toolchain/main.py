import argparse
import serial_manager
import config
import operations
import sys

# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Toolchain for managing the Olimexino-32u4")
    choices = [
        "compile_bootloader",
        "compile_application",
        "select_com",
        "install_programmer",
        "install_bootloader",
        "load_application",
        "read_memory",
        ]
    parser.add_argument("command", choices=choices, help="Command to execute")
    
    args = parser.parse_args()

    selected_com = config.load_selected_com()

    try:
        requested = choices.index(args.command)
        index = choices.index("select_com")
        if requested >= index:
            if selected_com:
                print(f"Selected COM port: {selected_com}")
            else:
                print("No COM port selected.")
                print("Please select a COM port before proceeding.")
                sys.exit()
        else:
            print("This command does not require a COM port.")
            print("You can proceed.")

    except:
        print("Unknown command.")
        print("Cannot proceed.")
        sys.exit()

    match args.command:
        
        case "compile_bootloader":
            operations.compile_bootloader()

        case "compile_application":
            operations.compile_application()
        
        case "select_com":
            serial_manager.select_com_ports()
        
        case "install_programmer":
            operations.install_programmer(selected_com)

        case "install_bootloader":
            operations.install_bootloader(selected_com)
            operations.lock_memory_read(selected_com)
        
        case "load_application":
            operations.load_application(selected_com)
        
        case "read_memory":
            operations.read_memory(selected_com)
        

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
