"""
The Program is HomuraMC Setup Script.

Commands:
    python setup.py req   install HomuraMC Dependencies.
"""

import argparse
import subprocess

ap = argparse.ArgumentParser(description="The Program is HomuraMC Setup Script.")

ap.add_argument("cmd", help="Commands to execute")

arg = ap.parse_args()

if arg.cmd == "req":
    subprocess.run("pip install -r requirements.txt", shell=True)
