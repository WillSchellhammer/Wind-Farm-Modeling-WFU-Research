#
# Contact: Will Schellhammer, schewb24@wfu.edu
# Updated: 4/2/2026
# WORK IN PROGRESS
import subprocess

# -----------------------------------------------------------------------------------------
# Settings
windSpeed = 11 # m/s, match with TurbSim file
analysisTime = 1800 # seconds, should be <= TurbSim analysis time
templateFSTF = "..\\FAST.Farm.fstf" # Edits the TEMPLATE .fstf file
fileFST = "FFTest_WT1.fst"
fileIW = "IW.dat"
fileElastoDyn = "NRELOffshrBsline5MW_Onshore_ElastoDyn_8mps.dat"
fileTurbSimBTS = "TurbSim3.bts"

# -----------------------------------------------------------------------------------------
# Variables

# -----------------------------------------------------------------------------------------
# Functions
def UpdateFiles():
    # Update TEMPLATE .fstf file (one directory behind)
    print (f"Updating template .fstf file {templateFSTF}")
    with open(templateFSTF, 'r') as file:
        lines = file.readlines()
        file.close()
    lines[5] = f"{analysisTime}                TMax               - Total run time (s) [>=0.0]\n"
    lines[33] = f"\"{fileIW}\"           InflowFile         - Name of file containing InflowWind module input parameters\n"
    with open (templateFSTF, 'w') as file:
        file.writelines(lines)
        file.close()

    # Update .fst file
    print (f"Updating .fst file {fileFST}")
    with open(fileFST, 'r') as file:
        lines = file.readlines()
        file.close()
    lines[5] = f"        {analysisTime}   TMax            - Total run time (s)\n"
    lines[33] = f"\"{fileElastoDyn}\"    EDFile          - Name of file containing ElastoDyn input parameters (quoted string)\n"
    lines[37] = f"\"{fileIW}\"    InflowFile      - Name of file containing inflow wind input parameters (quoted string)\n"
    with open (fileFST, 'w') as file:
        file.writelines(lines)
        file.close()

    # Update IW file
    print (f"Updating IW file {fileIW}")
    with open (fileIW, 'r') as file:
        lines = file.readlines()
        file.close()
    lines[21] = f"\"{fileTurbSimBTS}\" FileName_BTS  - Name of the Full field wind file to use (.bts)\n"
    lines[45] = f"          {windSpeed}   URef           - Mean u-component wind speed at the reference height (m/s)\n"
    with open (fileIW, 'w') as file:
        file.writelines(lines)
        file.close()

    # # Update ElastoDyn file
    # print (f"Updating ElastoDyn file {fileElastoDyn}")
    # with open (fileElastoDyn, 'r') as file:
    #     lines = file.readlines()
    #     file.close()
    # lines[32] = f"        {windSpeed}   RotSpeed    - Initial or fixed rotor speed (rpm)\n"
    # with open (fileElastoDyn, 'w') as file:
    #     file.writelines(lines)
    #     file.close()

    print ("File updates finished.")

def RotateFarm():
    print("\nRunning RotateFarm.py")
    subprocess.run(["python", "RotateFarm.py"])

def Multiparser():
    print("\nRunning Multiparser.py")
    subprocess.run(["python", "Multiparser.py"])

print("Starting...\n")
UpdateFiles()
RotateFarm()
Multiparser()
print("\nFinished!")