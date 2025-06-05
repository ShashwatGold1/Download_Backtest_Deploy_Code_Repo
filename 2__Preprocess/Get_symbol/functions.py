import pandas as pd
import numpy as np
import json

def add_strike_prices_in_new_column(time_value, unique_symbols_CE, df):
    df_strike_price = pd.DataFrame()
    # Create datetime column if not exists
    if 'datetime' not in df.columns:
        # Convert to datetime and ensure it's datetime type, not string
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y-%m-%d %H:%M:%S')
    
    # Get the date from first row and create target time
    today_date = pd.to_datetime(df['datetime'].iloc[0]).date()
    target_time = pd.to_datetime(f"{today_date} {time_value}")
    
    for nn in range(0, len(unique_symbols_CE)):
        symbol = unique_symbols_CE[nn]
        
        # Filter df for the specific symbol
        df_of_one_symbol = df[df.symbol == symbol].copy()
        
        # Find the closest time match
        closest_time_idx = (pd.to_datetime(df_of_one_symbol['datetime']) - target_time).abs().idxmin()
        strike_price = df_of_one_symbol.loc[closest_time_idx, 'close']
        
        # Convert numpy.int64 to int if needed
        if isinstance(strike_price, np.int64):
            strike_price = int(strike_price)
        
        # Assign strike_price to the corresponding row
        df_strike_price.loc[nn, 'symbol'] = symbol
        df_strike_price.loc[nn, 'strike_price'] = strike_price

    df_strike_price['time'] = time_value

    return df_strike_price

def find_nearest_greater(df):
    # Filter out strike prices less than 270
    filtered_df_CE = df[(df['strike_price'] < 270)]
    
    # If there are no such values, return None
    if filtered_df_CE.empty:
        return None
    
    # Find the maximum strike price that is less than 270
    CE_strike = filtered_df_CE[filtered_df_CE['strike_price'] == filtered_df_CE['strike_price'].max()]
    
    return CE_strike

def update_date_records(aa_a, bb_b):
    
    file_path = r"date_records.json"
    new_record = {"date": aa_a, "processed_on": bb_b}

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("JSON file is not in list format.")
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    updated = False
    for record in data:
        if record.get("date") == aa_a:
            record["processed_on"] = bb_b 
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
        with open("date_records.json", "r") as file:
            data = json.load(file)
            
        for record in data:
            if record["date"] == date_to_check:
                return "date_found"
        return "date_not_found"
            
    except (FileNotFoundError, json.JSONDecodeError):
        return "date_not_found"
