import json
import pandas as pd

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
