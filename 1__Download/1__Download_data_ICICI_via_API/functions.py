import json
from datetime import datetime, timedelta
import pandas as pd
import socket
import time
from IPython.display import display, HTML, Javascript

def get_line(file_name_, line_number):
    try:
        with open(file_name_, 'r') as f:
            for current_line, content in enumerate(f, start=1):
                if current_line == line_number:
                    return content.strip()
        # If the function hasn't returned yet, the line was not found
        print(f"Line {line_number} not found.")
        return None
    except OSError as e:  # handle file-related exceptions
        # print_plus(f"OS error: {e}", False, f'{file_name}_output.txt', True)
        print(f"OS error: {e}")
        return None

def update_line(file_name, line_number, data):
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
        lines[line_number - 1] = json.dumps(data) + "\n"
        with open(file_name, 'w') as file:
            file.writelines(lines)
    except (OSError, IndexError) as e:
        print(f"Error: {e}")

def get_next_five_dates(input_date):
    """
    Get 5 weekday dates from the same week in order: Thursday, Wednesday, Tuesday, Monday, Friday
    Excludes holidays listed in D:/Programming/Download_Backtest_Deploy_data/1__Download/1__Download_data_ICICI_via_API/holidays.json
    
    Args:
        input_date (str): Date in format '2020-01-06T09:15:00.000Z'
    Returns:
        list: List of weekday dates (excluding holidays) in format 'YYYY-MM-DDT07:00:00.000Z'
    """
    # Load holidays
    with open('D:/Programming/Download_Backtest_Deploy_data/1__Download/1__Download_data_ICICI_via_API/holidays.json', 'r') as file:
        holidays = json.load(file)
    
    # Parse input date
    date_obj = datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S.000Z")
    
    # Get to Monday of the week
    while date_obj.weekday() != 0:  # 0 is Monday
        date_obj -= timedelta(days=1)
    
    # Create weekday map for the week, excluding holidays
    week_dates = {}
    for i in range(5):  # Monday to Friday
        current_date = date_obj + timedelta(days=i)
        if current_date.strftime('%Y-%m-%d') not in holidays:
            week_dates[i] = current_date
    
    # Return dates in desired order: Thu, Wed, Tue, Mon, Fri
    order = [3, 2, 1, 0, 4]  # Thu, Wed, Tue, Mon, Fri
    dates = []
    
    for day in order:
        if day in week_dates:
            dates.append(week_dates[day].strftime("%Y-%m-%dT07:00:00.000Z"))
    
    return dates

def generate_range(start, end):
    """
    Generate a list of numbers in increments of 50, starting from the nearest multiple of 50
    greater than or equal to 'start' and ending at the nearest multiple of 50 less than or equal to 'end'.
    
    Parameters:
    start (float): The starting value.
    end (float): The ending value.
    
    Returns:
    list: A list of numbers in the specified range.
    """
    start_n = start if start < end else end
    end_n = end if end > start else start

    # Calculate the nearest multiples of 50
    start_n = (start_n + 49) // 50 * 50  # Round up to the nearest multiple of 50
    end_n = end_n // 50 * 50  # Round down to the nearest multiple of 50
    
    # Generate the range
    return list(range(int(start_n), int(end_n) + 1, 50))

def get_monday_timestamps():
    """
    Generate DataFrame of Monday dates (or next working day if Monday is holiday)
    from 2020-01-01 to today with specific timestamps
    Returns DataFrame with columns 'start_time' and 'end_time'
    """
    # Load holidays
    with open('D:/Programming/Download_Backtest_Deploy_data/1__Download/1__Download_data_ICICI_via_API/holidays.json', 'r') as file:
        holidays = json.load(file)
    
    # Set start and end dates
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    
    # Create lists to store timestamps
    monday_data = []
    
    # Find first Monday
    while start_date.weekday() != 0:  # 0 represents Monday
        start_date += timedelta(days=1)
    
    # Generate all Mondays
    current_date = start_date
    while current_date <= end_date:
        # Find next working day if Monday is holiday
        working_date = current_date
        while (working_date.strftime('%Y-%m-%d') in holidays or 
               working_date.weekday() >= 5):  # Check for holidays and weekends
            working_date += timedelta(days=1)
        
        # Format timestamps for working day
        start_time = working_date.replace(hour=9, minute=15, second=0, microsecond=0)
        end_time = working_date.replace(hour=9, minute=16, second=0, microsecond=0)
        
        # Add to data list
        monday_data.append({
            'start_time': start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            'end_time': end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
        
        # Move to next Monday
        current_date += timedelta(days=7)
    
    # Create DataFrame
    df_mondays = pd.DataFrame(monday_data)
    return df_mondays

def get_row_by_date(dataframe, target_date):
    """
    Get row index and data for a specific date from a DataFrame
    
    Args:
        dataframe: DataFrame containing the data
        target_date: Date to search for in format 'YYYY-MM-DD'
        
    Returns:
        tuple: (row_index, row_data) or (None, None) if date not found
    """
    # Convert datetime column to date string format for comparison
    if 'date' in dataframe.columns:
        # Try to find exact match first
        mask = dataframe['date'].str.startswith(target_date)
        matches = dataframe[mask]
        
        if not matches.empty:
            row_index = matches.index[0]
            return row_index-len(dataframe), matches.iloc[0]
            
    return None, None

def generate_15_min_intervals(date_str):
    """
    Generate 15-minute intervals between 9:15 and 15:30 for given date
    
    Args:
        date_str (str): Date in format 'YYYY-MM-DDT07:00:00.000Z'
    Returns:
        list: List of datetime strings in 15-minute intervals
    """
    # Parse input date and set start/end times
    base_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    start = datetime.combine(base_date, datetime.strptime("09:15", "%H:%M").time())
    end = datetime.combine(base_date, datetime.strptime("15:30", "%H:%M").time())
    
    intervals = []
    current = start
    
    while current <= end:
        intervals.append(current.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z")
        current += timedelta(minutes=15)
        
    return intervals

def get_last_eight_weekdays(input_date):
    """
    Get last 8 dates excluding weekends from the given date (including input date)
    
    Args:
        input_date (str): Date in format '2021-08-26T07:00:00.000Z'
    Returns:
        list: List of weekday dates in format 'YYYY-MM-DDT07:00:00.000Z'
    """
    # Parse input date
    end_date = datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S.000Z")
    
    dates = []
    days_checked = 0
    while len(dates) < 6:
        current_date = end_date - timedelta(days=days_checked)
        # Check if day is not Saturday (5) or Sunday (6)
        if current_date.weekday() < 5:
            dates.append(current_date.strftime("%Y-%m-%dT07:00:00.000Z"))
        days_checked += 1
    
    # Reverse list to get dates in ascending order
    dates.reverse()
    return dates

def get_all_weekdays(start_date):
    """
    Generate all weekday dates from 2020-01-01 to today, excluding holidays
    Returns list of dates in format 'YYYY-MM-DDT07:00:00.000Z'
    """
    with open('D:/Programming/Download_Backtest_Deploy_data/1__Download/1__Download_data_ICICI_via_API/holidays.json', 'r') as file:
        holidays = json.load(file)

    # Set start and end dates
    start_date = start_date
    end_date = datetime.now()
    
    weekday_dates = []
    current_date = start_date
    
    while current_date < end_date:
        # Check if day is not Saturday (5) or Sunday (6) and not a holiday
        if current_date.weekday() < 5 and current_date.strftime('%Y-%m-%d') not in holidays:
            weekday_dates.append(current_date.strftime("%Y-%m-%dT07:00:00.000Z"))
        current_date += timedelta(days=1)
    
    return weekday_dates

def find_next_expiry_date(input_date):
    """
    Find the nearest equal or greater date from expiry dates list
    
    Args:
        input_date (str): Date in format 'YYYY-MM-DDT07:00:00.000Z'
    Returns:
        str: Nearest equal or greater expiry date
    """
    # Read expiry dates from JSON file
    with open('D:/Programming/Download_Backtest_Deploy_data/1__Download/1__Download_data_ICICI_via_API/expiry_dates_list_code.json', 'r') as file:
        expiry_dates = json.load(file)
    
    # Convert input date to datetime
    input_dt = datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Find next expiry date
    next_date = None
    for date in expiry_dates:
        expiry_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        if expiry_dt >= input_dt:
            next_date = date
            break
    
    return next_date

def get_nearest_midpoint(row):
    """
    Calculate midpoint between high_plus_1000 and low_minus_1000,
    then find nearest multiple of 50
    
    Args:
        row: DataFrame row containing high_plus_1000 and low_minus_1000
    Returns:
        float: Nearest multiple of 50 to the midpoint
    """
    # Calculate midpoint
    midpoint = (row['high_plus_1000'] + row['low_minus_1000']) / 2
    
    # Find nearest multiple of 50
    nearest_50 = round(midpoint / 50) * 50
    
    return nearest_50

def generate_range_for_expiry_date(value, base_value=1000, defalt_range=5):
    """
    Generate range values with original value first, followed by alternating higher/lower values
    
    Args:
        value (float/int): The input value to include at start
    Returns:
        list: List with alternating higher/lower values from the center
    """
    # Generate base values in steps of 1000
    base = round(value/base_value) * base_value
    higher_values = [base + (i * base_value) for i in range(1, defalt_range+1)]  # Above base
    lower_values = [base - (i * base_value) for i in range(1, defalt_range+1)]   # Below base
    
    # Create result with alternating values
    result = [value]
    for i in range(defalt_range):
        result.append(higher_values[i])  # Add next higher value
        result.append(lower_values[i])   # Add next lower value
    
    return result

def generate_symmetric_range(value, base_value=1000, default_range=5):
    """
    Generate a symmetric range of values around the base value until reaching zero on the lower side.
    The same number of values are generated on the higher side.
    
    Args:
        value (float/int): The input value to include at start
        base_value (int): The step value for generating the range
        default_range (int): The initial count of values to be generated on each side
    
    Returns:
        list: Symmetric list with values decreasing to zero and extending equally on the higher side
    """
    base = round(value / base_value) * base_value
    lower_values = []
    
    # Generate lower values till 0
    current_value = base
    while current_value > 0:
        lower_values.append(current_value)
        current_value -= base_value
    lower_values.append(0)  # Ensure 0 is included
    
    # Ensure symmetric higher values
    higher_values = [base + (i * base_value) for i in range(1, len(lower_values))]
    
    # # Merge values in alternating order
    # result = [value]
    # for i in range(len(lower_values)):
    #     if i < len(higher_values):
    #         result.append(higher_values[i])
    #     if i < len(lower_values):
    #         result.append(lower_values[i])
    
    return [value] + higher_values + lower_values

def update_date_records(aa_a, bb_b):
    
    file_path = r"D:/Programming/Download_Backtest_Deploy_data/1__Download/1__Download_data_ICICI_via_API/date_records.json"
    new_record = {"processed_dates": aa_a, "downloaded_data_on": bb_b}

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("JSON file is not in list format.")
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    updated = False
    for record in data:
        if record.get("processed_dates") == aa_a:
            record["downloaded_data_on"] = bb_b 
            updated = True
            break

    if not updated:
        data.append(new_record)  # Append new record if not found

    # Save updated data back to the file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

    # print("Record updated successfully!" if updated else "New record added successfully!")

def check_date_in_records(date_to_check):
    try:
        with open("D:/Programming/Download_Backtest_Deploy_data/1__Download/1__Download_data_ICICI_via_API/date_records.json", "r") as file:
            data = json.load(file)
            
        for record in data:
            if record["processed_dates"] == date_to_check:
                return "date_found"
        return "date_not_found"
            
    except (FileNotFoundError, json.JSONDecodeError):
        return "date_not_found"

def update_element(s):
    display(HTML("""<div><pre id="clock" style='margin:0; padding:0;'></pre></div>"""))
    display(Javascript(f"""document.getElementById('clock').innerHTML = '{s}';"""))

def is_internet_available():

    starting_time = str(datetime.now())
    start_time = datetime.strptime(starting_time, "%Y-%m-%d %H:%M:%S.%f")

    time_elapsed = None

    while True:
        try:
            # Attempt to connect to Google's DNS server
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            if time_elapsed is not None:
                print(f"Successfully connected to the internet after 0{time_elapsed}")
            print(f"Internet Connection: 'Available'")
            return True
        except OSError:
            
            current_time = datetime.now()
            time_elapsed = str(current_time - start_time).split('.')[0]

            update_element(f"Internet connection lost, retrying... Time Elapsed: 0{time_elapsed}")

            time.sleep(1)

# import sys
# from io import StringIO
# from IPython.display import clear_output

# old_stdout = sys.stdout
# captured_output = StringIO()
# sys.stdout = captured_output

# # Your code that produces output
# print("This is some output", df)
# print("This is some output", df)

# output_text = captured_output.getvalue()
# sys.stdout = old_stdout
# clear_output(wait=True)

# print("Previously captured output:")
# print(output_text)