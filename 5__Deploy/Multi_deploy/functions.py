import json
import pandas as pd
import keyboard
import random
import time
from dhanhq import MarketFeed
import winsound
import os

import sys; sys.path.append('..')
from config import MYPATHS

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

# ==========================================================================================
# ==========================================================================================

def update_line(file_name, line_number, data):
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
        lines[line_number - 1] = json.dumps(data) + "\n"
        with open(file_name, 'w') as file:
            file.writelines(lines)
    except (OSError, IndexError) as e:
        print(f"Error: {e}")

# ==========================================================================================
# ==========================================================================================

def bidirectional_loop(start_idx, df_length):
    """Generate indices in bidirectional pattern from start_idx"""
    yield start_idx
    
    for offset in range(1, df_length):
        # Go left first
        if start_idx - offset >= 0:
            yield start_idx - offset
        # Then go right
        if start_idx + offset < df_length:
            yield start_idx + offset

# ==========================================================================================
# ==========================================================================================

def convert_candles(df, symbol_name):
    """
    Convert 1-minute OHLC data to 3-minute candles for a single symbol
    Uses exact same logic as convert_1_second_data.ipynb
    
    Args:
        df: DataFrame with columns ['datetime', 'open', 'high', 'low', 'close', 'volume', 'open_interest']
        symbol_name: String name of the symbol
    
    without open_interest column
        
    Returns:
        DataFrame with 3-minute candles
    """
    
    # Ensure datetime is in correct format
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    
    # Set datetime as index for resampling
    df_indexed = df.set_index('datetime')
    
    # Resample to 3-minute candles using exact same aggregation logic
    resampled = df_indexed.resample('3T').agg({
        'open': 'first',
        'high': 'max', 
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Add symbol column
    resampled['symbol'] = symbol_name
    
    # Reset index and reorder columns
    result = resampled.reset_index()
    result = result[['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
    
    return result

# ==========================================================================================
# ==========================================================================================

def create_nifty_symbol(underlying, latest_expiry, month, strike, option_type):

    return f"{underlying}{latest_expiry[-2:]}{month}{latest_expiry[-8:-6]}{strike}{option_type}".replace("CALL", "CE").replace("PUT", "PE")

# ==========================================================================================
# ==========================================================================================

from datetime import datetime, timedelta
import socket
from IPython.display import display, HTML, Javascript
import time

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
            print(f"🌐 Internet Connection: 'Available'")
            return True
        except OSError:
            
            current_time = datetime.now()
            time_elapsed = str(current_time - start_time).split('.')[0]

            update_element(f"Internet connection lost, retrying... Time Elapsed: 0{time_elapsed}")

            time.sleep(1)

# ==========================================================================================
# ==========================================================================================

def printk(message, condition=True):
    """Custom print function for better readability"""
    if condition:
        print(message)

# ==========================================================================================
# ==========================================================================================

def prevent_sleep_with_win_search(interval=150):
    # preventing the Internet Connection Loss

    # Sample search terms (you can expand this list)
    search_terms = [
        "cmd", "notepad", "calc", "python", "edge",
        "paint", "settings", "task manager", "snipping tool",
        "control panel", "windows update", "event viewer"
    ]

    try:
        while True:
            term = random.choice(search_terms)

            # Press Windows key
            keyboard.press_and_release('windows')
            time.sleep(0.5)

            # Type search term
            keyboard.write(term, delay=0.05)
            time.sleep(1)

            # Press Esc to close Start menu
            keyboard.press_and_release('esc')

            # Wait until next iteration
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped.")

# ==========================================================================================
# ==========================================================================================

def get_prices_under_1000(df):
    first_ce_idx = df[df['ce_last_price'] >= 800].index.max()
    first_pe_idx = df[df['pe_last_price'] >= 800].index.min()
    filtered_df = df[first_ce_idx:first_pe_idx].reset_index(drop=True)
    
    ce_cols = ['security_id_CE', 'ce_iv', 'ce_volume', 'ce_oi', 'ce_last_price']
    pe_cols = ['pe_last_price', 'pe_iv', 'pe_oi', 'pe_volume', 'security_id_PE']
    
    filtered_df.loc[filtered_df['ce_last_price'] < 50, ce_cols] = 0.0
    filtered_df.loc[filtered_df['pe_last_price'] < 50, pe_cols] = 0.0
    
    return filtered_df

def create_instruments_from_df(df):
    instruments = []
    for _, row in df.iterrows():
        if pd.notna(row['security_id_CE']) and row['security_id_CE'] != 0.0:
            instruments.append((MarketFeed.NSE_FNO, str(int(row['security_id_CE'])), MarketFeed.Ticker))
        if pd.notna(row['security_id_PE']) and row['security_id_PE'] != 0.0:
            instruments.append((MarketFeed.NSE_FNO, str(int(row['security_id_PE'])), MarketFeed.Ticker))
    return instruments

# ==========================================================================================
# ==========================================================================================

def play_sound(file_name, error_message, print_error):

    # Alert_01, Alert_02, Atma_rama_Alarm
    sound_path = os.path.join(MYPATHS['Audio_files'], f"{file_name}.wav")

    if not os.path.isfile(sound_path):
        print(f"\033[1;31mSound file not found: {sound_path}\033[0m")
        if print_error == "error": raise FileNotFoundError(f"Missing sound file: {sound_path}")
        return

    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    print(f"\033[1;31m{error_message}\033[0m")

    if print_error == "error":
        raise Exception(f"\033[1;31m{error_message}\033[0m")
