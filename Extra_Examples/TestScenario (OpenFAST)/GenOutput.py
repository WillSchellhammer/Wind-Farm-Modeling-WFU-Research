# Generates output files from OpenFast simulations
# The wind input file increases in number by one each time until no more wind files are available
# Contact: Will Schellhammer, schewb24@wfu.edu
# Created: 10/15/2025
# WORK IN PROGRESS

import os.path
import subprocess

openfastEXE = "openfast_x64.exe"
openfastARG = "MinimalExample/Main.fst"
inflowFile = "MinimalExample/InflowWind_IncrementBTS.dat"
iteration = 1
windFile = "Custom_Wind/TurbSim" + str(iteration) + ".bts" #set to the test wind file by default

# Test if the test wind file exists
while os.path.exists(windFile):
    print("Reading " + windFile)

    # Change wind file location in Inflow Wind file
    if not os.path.exists(inflowFile):
        print("The file " + inflowFile + " does not exist. Ending program abnormally.")
        exit(2) # Exit code 2, input file not found
    with open(inflowFile, 'r') as file:
        lines = file.readlines()
    lines[21] = "\"../" + windFile + "\"    FileName_BTS   - Name of the Full field wind file to use (.bts)\n"
    with open(inflowFile[0:len(inflowFile)-4] + str(iteration) + ".dat", 'w') as file:
        file.writelines(lines)
    with open(openfastARG, 'r') as file:
        lines = file.readlines()
    lines[37] = "\"" + inflowFile[inflowFile.index('/')+1:len(inflowFile)-4] + str(iteration) + ".dat" + "\"      InflowFile      - Name of file containing inflow wind input parameters (quoted string)\n"
    with open(openfastARG[0:len(openfastARG)-4] + str(iteration) + ".fst", 'w') as file:
        file.writelines(lines)

    # Run OpenFast
    result = subprocess.run([openfastEXE, openfastARG[0:len(openfastARG)-4] + str(iteration) + ".fst"], capture_output=True, text=True)

    # Print OpenFast command line output to the openfastLog.txt
    with open("Logs/openfastLog" + str(iteration) + ".txt", 'w') as file:
        file.write("OPENFAST OUTPUT: " + result.stdout + "\n")
        file.write("OPENFAST ERROR: " + result.stderr + "\n")
        file.write("RETURN CODE: " + str(result.returncode) + "\n")

    # Change the wind file with the new number
    iteration += 1
    windFile = windFile[:len(windFile)-4-len(str(iteration-1))] + str(iteration) + windFile[len(windFile)-4:]


print("The file " + windFile + " does not exist. Ending program normally.")

