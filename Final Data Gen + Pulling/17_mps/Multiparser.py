# Runs FAST.Farm for every fstf file for each .bts
# Contact: Will Schellhammer, schewb24@wfu.edu
# Updated: 3/31/2026

import os
import subprocess

# -----------------------------------------------------------------------------------------
# Settings
fastEXE = "..\\FAST.Farm_x64.exe"
stopAfter = 5 # set to -1 to disable

# -----------------------------------------------------------------------------------------
# Variables
iteration = 0

# -----------------------------------------------------------------------------------------
# Functions
def runFSTF():
    global iteration
    root_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.abspath(os.path.join(root_dir, fastEXE))

    # Walk through the directory tree
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if iteration >= stopAfter and stopAfter != -1: break # end program early

            if file.endswith(".fstf"):
                iteration += 1
                # ... rest of your subprocess code ...
                # Construct the full path to the file
                file_path = os.path.join(root, file)

                print(f"Processing: {file_path}")

                try:
                    # 'root' is the directory containing the current .fstf file
                    # We use cwd=root so the subprocess executes inside that directory
                    log_file = f"{file}.log"
                    command = f"& '{exe_path}' '{file}' | Tee-Object -FilePath '{log_file}'"
                    result = subprocess.run(
                        ["powershell", "-Command", command],
                        cwd=root,
                        check=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    print(f"Error for {file}: {result.stdout}. FAST Log saved as {log_file}")

                except subprocess.CalledProcessError as e:
                    print(f"  [FAILED] {file}. Check log to troubleshoot. Error: {e}")

                except FileNotFoundError:
                    print("Error: The file 'FAST.Farm_x64.exe' was not found.")
                    return

# -----------------------------------------------------------------------------------------
# Main Code

if __name__ == "__main__":
    runFSTF()

print(f"\nMultiparser complete.")