import sys
import subprocess
import os

# Imposto PYTHONPATH al subprocess
env = os.environ.copy()
env["PYTHONPATH"] = os.path.abspath("lib")

# Eseguo PyInstaller come modulo
subprocess.run([
    sys.executable, "-m", "nuitka",
    "--assume-yes-for-downloads",
    "--product-name=Peak2Sheet",
    "--product-version=1.0.0",
    "--file-version=1.0.0",
    "--mode=app",
    "--include-data-dir=gui=gui",
    "--output-dir=dist/windows",
    "--windows-console-mode=disable",
    "main.py",
], check=True, env=env)
