# FAST.Farm Farm Rotation Script - ATOMIC ISOLATION VERSION
# Contact: Will Schellhammer, schewb24@wfu.edu
# Updated: 3/30/2026

import math
import copy

# -----------------------------------------------------------------------------------------
# Variables
numIterations = 5  
ThetaInit = 0     
ThetaMod = 45      

# THE SOURCE OF TRUTH (READ-ONLY)
templateFile = "Fast.Farm.fstf" # Note: Reads a directory behind what's typed here

# -----------------------------------------------------------------------------------------
# Main Code

# 1. READ THE TEMPLATE ONCE AND STORE IT IN A PROTECTED VARIABLE
try:
    with open(f"..\\{templateFile}", 'r') as file:
        original_lines = file.readlines()
    print(f"Successfully loaded template: {templateFile}")
except FileNotFoundError:
    print(f"Error: {templateFile} not found.")
    exit(2)

# -----------------------------------------------------------------------------------------
for i in range(1, numIterations + 1):
    theta = ThetaInit + (i - 1) * ThetaMod
    rad = math.radians(theta)
    
    # OUTPUT NAME IS DISTINCT
    out_name = f"FAST.Farm_{theta}.fstf"
    
    # 2. CREATE A DEEP COPY OF THE DATA SO WE DON'T TOUCH THE ORIGINAL LIST
    new_lines = copy.deepcopy(original_lines)

    # 3. LOCATE TURBINE TABLE
    start_idx = 0
    for idx, line in enumerate(new_lines):
        if "WT_X" in line and "WT_Y" in line:
            start_idx = idx + 2 
            break

    # 4. ROTATE DATA IN THE COPY
    j = 0
    while True:
        line_idx = start_idx + j
        try:
            values = new_lines[line_idx].split()
            if not values or len(values) < 10: break # Ensure it's a full turbine line
            
            wt_x_orig = float(values[0])
            wt_y_orig = float(values[1])
            
            # Rotate Position (Counter-Clockwise)
            wt_x_rot = wt_x_orig * math.cos(rad) - wt_y_orig * math.sin(rad)
            wt_y_rot = wt_x_orig * math.sin(rad) + wt_y_orig * math.cos(rad)

            # Re-center High-Res Box using the 10.17-based offset
            # Using 76.275 ensures the turbine is dead-center in the 16x16 grid
            x0_h_rot = wt_x_rot - 76.275
            y0_h_rot = wt_y_rot - 76.275

            # Re-format line
            # Force values[7] and values[8] to 10.17 to be safe
            new_lines[line_idx] = (
                f"{wt_x_rot:<12.3f} {wt_y_rot:<12.3f} {values[2]:<8} {values[3]:<18} "
                f"{x0_h_rot:<12.3f} {y0_h_rot:<12.3f} {values[6]:<8} 10.17    10.17    "
                f"{values[9]:<8}\n"
            )
            j += 1
        except (IndexError, ValueError):
            break

    # 5. WRITE ONLY TO THE NEW FILENAME
    with open(out_name, 'w') as file:
        file.writelines(new_lines)
    print(f"Generated: {out_name}")

print(f"\nRotateFarm completed.")