import os
import json
import ast
from pathlib import Path
from datetime import datetime

# Hard-coded base path - change this line for different setups
BASE_PATH = Path("D:/Programming/Download_Backtest_Deploy_data/5__Deploy/Multi_deploy")

# All paths in one place
MYPATHS = {
    'base': str(BASE_PATH),
    'data': str(BASE_PATH / "data"),
    'Audio_files': str(BASE_PATH / "Audio_files"),
    'Live_Tick_Data': str(BASE_PATH / "Live_Tick_Data"),
    'Option_Chain_with_Security_id': str(BASE_PATH / "Raw_Simulation_data" / "Option_Chain_with_Security_id"),
    'Raw_data_bin': str(BASE_PATH / "Raw_Simulation_data" / "Raw_data_bin"),
    'Raw_data_txt': str(BASE_PATH / "Raw_Simulation_data" / "Raw_data_txt"),
    'Simulation_Tick_Data': str(BASE_PATH / "Simulation_Tick_Data")
}

# Other data
XDATA = {
    'Analysis_date': '2025-06-26'
}