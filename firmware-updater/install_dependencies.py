import sys
import os
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))

subprocess.run(
    cwd=script_dir,
    args=[
        sys.executable, "-m", "pip", "install",
        "--target", "lib",
        "-r", "requirements.txt"
    ],
)
