import serial
import serial.tools.list_ports
from config import save_selected_com

def select_com_ports():
    """List all available COM ports and allow the user to select one."""
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No COM ports found.")
        return

    print("Available COM ports:")
    for i, port in enumerate(ports):
        print(f"[{i}] {port.device} - {port.description}")
    
    while True:
        try:
            choice = 0
            if len(ports) > 1:
                choice = int(input("Select the desired COM port number: "))
            if 0 <= choice < len(ports):
                selected_port = ports[choice].device
                save_selected_com(selected_port)
                print(f"You selected: {selected_port}")
                break
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Enter a valid number.")

