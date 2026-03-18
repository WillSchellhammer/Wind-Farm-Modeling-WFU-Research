# Generates wind files from TurbSim simulations
# Contact: Will Schellhammer, schewb24@wfu.edu
# Created: 10/29/2025
# WORK IN PROGRESS

import os
import random
import subprocess
import time

numIterations = 3 # Number of different scenarios to produce
URefInit = 8 # Starting URef (m/s)
URefMod = 0 # How much to increase URef by per iteration (m/s)
WindDirInit = -10 # Starting HFlowAng of wind (degrees)
WindDirMod = 10 # How much to increase HFlowAng by per iteration (degrees)
turbsimEXE = "TurbSim_x64.exe" # TurbSim exe file location
turbsimINP = "TurbSim.inp" # TurbSim input file location
numGrid = 31 # must match turbsimIMP file, both x and y
gridLength = 163 # meters, must match turbsimIMP file, both height and width (163 minimum for NREL 5MW baseline (found through trial/error))
rotorRadius = 126/2 # meters, diameter of 126 for 5 MW turbine
hubHeight = 90 # meters, must match turbsimIMP file
# gridLength >= rotorRadius + hubHeight or genData will read nonexistent values

startTime = time.perf_counter()

# Generate wind files
for i in range (1,numIterations+1):
    # Read input file
    try:
        with open(turbsimINP, 'r') as file:
            inpLines = file.readlines()
            file.close()
    except FileNotFoundError:
        print("The file " + turbsimINP + " does not exist. Ending program.")
        exit(2) # Exit code 2, file not found
    # Change the seed for a new RNG
    inpLines[4] = str(random.randint(-2147483648, 2147483647)) + "      RandSeed1       - First random seed  (-2147483648 to 2147483647)\n"
    inpLines[39] = "         " + str(URefInit + (i-1)*URefMod) + "   URef            - Mean (total) velocity at the reference height [m/s] (or \"default\" for JET velocity profile) [must be 1-hr mean for API model; otherwise is the mean over AnalysisTime seconds]\n"
    inpLines[27] = "          " + str(WindDirInit + (i-1)*WindDirMod) + "  HFlowAng        - Horizontal mean flow (skew) angle [degrees]\n"

    print("Generating wind file " + str(i) + "...")
    turbsimINP = "Generator/TurbSim" + str(i) + ".inp"
    with open(turbsimINP, 'w') as file:
        file.writelines(inpLines)
    result = subprocess.run([turbsimEXE, turbsimINP], capture_output=True, text=True)
    with open("Generator/turbsimLog" + str(i) + ".txt", 'w') as file:
        file.write("TURBSIM OUTPUT: " + result.stdout + "\n")
        file.write("TURBSIM ERROR: " + result.stderr + "\n")
        file.write("RETURN CODE: " + str(result.returncode) + "\n")
    os.remove(turbsimINP[0:len(turbsimINP)-4] + ".v")
    os.remove(turbsimINP[0:len(turbsimINP)-4] + ".w")
    # Read wind velocities in the u direction from the .u file
    try:
        with open(turbsimINP[0:len(turbsimINP)-4] + ".u", 'r') as uFile:
            uLines = uFile.readlines()
    except FileNotFoundError:
        print("The file " + turbsimINP[0:len(turbsimINP)-4] + ".u" + " does not exist. This is likely due to an error while running TurbSim.")
    # Write training input data from the u file to the csv spreadsheet
    with open("Generator/genData" + str(i) + ".csv", 'w') as genData:
        genData.write("Point A,Point B,Point C,Point D,Point E\n")
        j = 13 # starting point of the first grid, line 14 in the .u file
        while j<len(uLines):
            dataAppend = ""
            # Equation for y: numGrid*(rotorRadius/gridLength)*sin(θ) + numGrid - numGrid(hubHeight/gridLength)
            # Equation for x: numGrid*(rotorRadius/gridLength)*cos(θ) + 1/2*numGrid
            # y is the first brackets, x is the second brackets
            dataAppend += uLines[j+ round(numGrid*((rotorRadius/gridLength)*-1.000000 + (1 - hubHeight/gridLength)))] [3+8*round(numGrid*(rotorRadius/gridLength)* 0.000000 + 0.5*numGrid) : 3+8*round(numGrid*(rotorRadius/gridLength)* 0.000000 + 0.5*numGrid)+6] + "," # Point A, Top-Center   point of star by 90-72*0 degrees
            dataAppend += uLines[j+ round(numGrid*((rotorRadius/gridLength)*-0.309017 + (1 - hubHeight/gridLength)))] [3+8*round(numGrid*(rotorRadius/gridLength)* 0.951057 + 0.5*numGrid) : 3+8*round(numGrid*(rotorRadius/gridLength)* 0.951057 + 0.5*numGrid)+6] + "," # Point B, Top-Right     point of star by 90-72*1 degrees
            dataAppend += uLines[j+ round(numGrid*((rotorRadius/gridLength)* 0.809017 + (1 - hubHeight/gridLength)))] [3+8*round(numGrid*(rotorRadius/gridLength)* 0.587785 + 0.5*numGrid) : 3+8*round(numGrid*(rotorRadius/gridLength)* 0.587785 + 0.5*numGrid)+6] + "," # Point C, Bottom-Right  point of star by 90-72*2 degrees
            dataAppend += uLines[j+ round(numGrid*((rotorRadius/gridLength)* 0.809017 + (1 - hubHeight/gridLength)))] [3+8*round(numGrid*(rotorRadius/gridLength)*-0.587785 + 0.5*numGrid) : 3+8*round(numGrid*(rotorRadius/gridLength)*-0.587785 + 0.5*numGrid)+6] + "," # Point D, Bottom-Left point of star by 90-72*3 degrees
            dataAppend += uLines[j+ round(numGrid*((rotorRadius/gridLength)*-0.309017 + (1 - hubHeight/gridLength)))] [3+8*round(numGrid*(rotorRadius/gridLength)*-0.951057 + 0.5*numGrid) : 3+8*round(numGrid*(rotorRadius/gridLength)*-0.951057 + 0.5*numGrid)+6] + "," # Point E, Top-Left    point of star by 90-72*4 degrees
            j += numGrid + 2 # go to next grid (there's a gap of 2 lines between each grid)
            genData.write(dataAppend + "\n")
    with open("Generator/fullData" + str(i) + ".csv", 'w') as genData:
        j = 12 # starting point of the first grid, line 14 in the .u file
        while j<len(uLines):
            dataAppend = ""
            # Equation for y: numGrid*(rotorRadius/gridLength)*sin(θ) + numGrid - numGrid(hubHeight/gridLength)
            # Equation for x: numGrid*(rotorRadius/gridLength)*cos(θ) + 1/2*numGrid
            # y is the first brackets, x is the second brackets
            for k in range(1, numGrid):
                dataAppend += uLines[j] [3 + 8*(k-1) : 3+8*k] + "," # Point A, Top-Center   point of star by 90-72*0 degrees
            j+=1
            genData.write(dataAppend + "\n")
print("Wind file generation complete! Ending program.")

endTime = time.perf_counter()

print("Runtime: " + str(round(endTime-startTime, 1)) + " seconds")

# (outdated)
# Run TurbSim
# result = subprocess.run([turbsimEXE, turbsimINP], capture_output=True, text=True)

# (outdated)
# Print TurbSim command line output to the latestLog.txt
# with open("latestLog.txt", 'w') as file:
#     file.write("TURBSIM OUTPUT: " + result.stdout + "\n")
#     file.write("TURBSIM ERROR: " + result.stderr + "\n")
#     file.write("RETURN CODE: " + str(result.returncode) + "\n")
