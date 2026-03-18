----------------------------------
OpenFAST Test Scenario (12/4/25)
Created by: Will Schellhammer (WFU Student)
----------------------------------

- How to run OpenFAST -

Option A: run.bat
- Runs one instance of OpenFAST using parameters from MinimalExample\Main.fst
- Outputs into MinimalExample\Main.out
- Graph the output file using MinimalExample\PlotSimulationResults.py by editing the variable outfile to 'Main.out'

Option B: GenOutput.py
- Runs as many instances of OpenFAST as there are wind files in Custom_Wind
- Outputs into MinimalExample\Main[#].out, replacing [#] with the instance number
- Graph an output file using MinimalExample\PlotSimulationResults.py by editing the variable outfile to 'Main[#].out'