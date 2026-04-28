import os
import subprocess
import shutil

# -----------------------------
# SETTINGS
# -----------------------------
numIterations = 3

URefInit = 7
URefMod = 0

WindDirInit = 8
WindDirMod = 0

fastfarmEXE = "../FAST.Farm_x64.exe"
template_fstf = "FAST.Farm.fstf"
iw_file = "IW.dat"

# -----------------------------
# 1. RUN TURBSIM ONCE
# -----------------------------
subprocess.run(["python", "GenWind_Ambient.py"])

# -----------------------------
# 2. LOOP FAST.FARM
# -----------------------------
for i in range(1, numIterations + 1):

    URef = URefInit + (i - 1) * URefMod
    WindDir = WindDirInit + (i - 1) * WindDirMod

    case_name = f"U{URef}_WD{WindDir}"
    case_dir = os.path.join("cases", case_name)

    print(f"\n--- {case_name} ---")

    bts_file = f"Generator_Ambient/TurbSim{i}.bts"

    if not os.path.exists(bts_file):
        print("Missing BTS file, skipping")
        continue

    os.makedirs(case_dir, exist_ok=True)

    # -----------------------------
    # UPDATE IW.dat (BTS FILE)
    # -----------------------------
    with open(iw_file, "r") as f:
        lines = f.readlines()

    for j in range(len(lines)):
        if "FileName_BTS" in lines[j]:
            lines[j] = f'"{bts_file}" FileName_BTS\n'

    with open(iw_file, "w") as f:
        f.writelines(lines)

    # -----------------------------
    # RUN FAST.FARM
    # -----------------------------
    subprocess.run([fastfarmEXE, template_fstf])

    # -----------------------------
    # MOVE OUTPUT FILES TO CASE DIR
    # -----------------------------
    for file in os.listdir():
        if file.endswith((".out", ".outb", ".ech", ".sum")):
            shutil.move(file, os.path.join(case_dir, file))

print("\nPipeline complete.")