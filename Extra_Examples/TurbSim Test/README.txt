----------------------------------
TurbSim Test (12/4/25)
Created by: Will Schellhammer (WFU Student)
----------------------------------

- How to run TurbSim -

Option A: run.bat
- Runs one instance of TurbSim using parameters from TurbSim.inp
- Outputs into TurbSim.wnd (wind file), TurbSim.bts (binary wind file), and TurbSim.sum (inputs summary)

Option B: GenWind.py
- Runs many instances of TurbSim with random seeds
- Edit parameters by editing variables within the GenWind.py script (see below) as well as editing the TurbSim.inp file in this folder
- Outputs each instance's input file, wind file, binary wind file, u-direction wind file, and summary file into the Generator folder, as well as fullData[#].csv and genData[#].csv (where [#] is the instance number]
- fullData.csv is the data from the u-direction wind file, genData.csv is only the data for 5 points in a circle around the hub (mimicing what a lidar scanner could measure)

=GenWind.py Key Parameters=
- numIterations: How many wind files to create
- URefInit: Mean wind speed of first wind file
- URefMod: Increases the mean wind speed by _____ m/s each wind file
- WindDirInit: Wind direction of first wind file
- WindDirMod: Increases the wind direction angle by _____ degrees each wind file