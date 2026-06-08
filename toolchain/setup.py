import subprocess
import sys

try:
    import serial
    import intelhex
except ImportError:
    print("dipendenze non trovate. Installazione in corso...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
