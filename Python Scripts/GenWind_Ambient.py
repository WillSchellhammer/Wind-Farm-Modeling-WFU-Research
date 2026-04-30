# Generates wind files from TurbSim simulations
# Contact: Will Schellhammer, schewb24@wfu.edu
# Created: 10/29/2025
# WORK IN PROGRESS

import os
import random
import subprocess
import time

# ----------------------------------------------------------------------------------------------------------------------
# Variables
numIterations = 5 # Number of different scenarios to produce
URefInit = 5 # Starting URef (m/s)
URefMod = 3 # How much to increase URef by per iteration (m/s)

turbsimEXE = "../TurbSim_x64.exe" # TurbSim exe file location
turbsimINP = "TurbSim.inp" # TurbSim input file location

# Only used when fullData = True
numGrid = 31 # Number of horizontal grid points in the u file

# ----------------------------------------------------------------------------------------------------------------------
# Settings
fullData = False # Writes u file data into a csv file
deleteU = True # Deletes the u file to save storage space

# ----------------------------------------------------------------------------------------------------------------------
# Functions

def writeFullData():
    with open("fullData" + str(i) + ".csv", 'w') as genData:
        j = 12
        while j<len(uLines):
            dataAppend = ""
            for k in range(1, numGrid):
                dataAppend += uLines[j] [3 + 8*(k-1) : 3+8*k] + ","
            j+=1
            genData.write(dataAppend + "\n")

# ----------------------------------------------------------------------------------------------------------------------
# Main Code
startTime = time.perf_counter()

for i in range (1,numIterations+1):

    try:
        with open(turbsimINP, 'r') as file:
            inpLines = file.readlines()
    except FileNotFoundError:
        print("The file " + turbsimINP + " does not exist. Ending program.")
        exit(2)

    # Random seed
    inpLines[4] = str(random.randint(-2147483648, 2147483647)) + "      RandSeed1\n"

    # Wind speed
    inpLines[39] = "         " + str(URefInit + (i-1)*URefMod) + "   URef\n"

    # FIXED wind direction (always 0)
    inpLines[27] = "          0  HFlowAng\n"

    print("Generating wind file " + str(i) + "...")

    turbsimINP = "TurbSim" + str(i) + ".inp"

    with open(turbsimINP, 'w') as file:
        file.writelines(inpLines)

    result = subprocess.run([turbsimEXE, turbsimINP], capture_output=True, text=True)

    with open("TurbSim" + str(i) + "Log.txt", 'w') as file:
        file.write("TURBSIM OUTPUT: " + result.stdout + "\n")
        file.write("TURBSIM ERROR: " + result.stderr + "\n")
        file.write("RETURN CODE: " + str(result.returncode) + "\n")

    os.remove(turbsimINP[0:len(turbsimINP)-4] + ".v")
    os.remove(turbsimINP[0:len(turbsimINP)-4] + ".w")

    try:
        with open(turbsimINP[0:len(turbsimINP)-4] + ".u", 'r') as uFile:
            uLines = uFile.readlines()
    except FileNotFoundError:
        print("The file " + turbsimINP[0:len(turbsimINP)-4] + ".u does not exist.")

    if fullData:
        writeFullData()

    if deleteU:
        os.remove(turbsimINP[0:len(turbsimINP)-4] + ".u")

print("Wind file generation complete! Ending program.")

endTime = time.perf_counter()
print("Runtime: " + str(round(endTime-startTime, 1)) + " seconds")