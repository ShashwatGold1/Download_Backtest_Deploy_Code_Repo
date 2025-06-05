import pandas as pd
import numpy as np
import mplfinance as mpf
import os
import matplotlib.pyplot as plt

def starting_ending(entry_i, exit_i, length):
    starting = entry_i - 20
    ending = entry_i + 80

    if starting < length:
        starting = length

    if ending < exit_i:
        ending = exit_i + 1

    if ending > -1:
        ending = -1

    return starting, ending

def get_nearest_lower_time(input_time):

    time_range = pd.date_range(start='09:15:00', end='15:30:00', freq='3T').strftime('%H:%M:%S')
    
    input_time_obj = pd.to_datetime(input_time).time()
    time_objects = [pd.to_datetime(t).time() for t in time_range]
    nearest_lower = max([t for t in time_objects if t <= input_time_obj], default=None)

    if nearest_lower:
        return nearest_lower.strftime('%H:%M:%S')
    
    return None

# def calculate_bollinger_bands_pctB(df, window_size=20):
#     rolling_mean = df["close"].rolling(window_size).mean()
#     rolling_std  = df["close"].rolling(window_size).std()

#     bollinger_df = df.copy()
#     bollinger_df['STD'] = round(rolling_std, 2)
#     bollinger_df['Middle'] = round(rolling_mean, 2)
#     bollinger_df['Upper'] = round(rolling_mean + (rolling_std * 2), 2)
#     bollinger_df['Lower'] = round(rolling_mean - (rolling_std * 2), 2)
#     bollinger_df['%B'] = (df["close"] - bollinger_df['Lower']) / (bollinger_df['Upper'] - bollinger_df['Lower'])

#     return bollinger_df

def calculate_bollinger_bands_pctB(df, window_size=20):
    bollinger_df = df.copy()

    # Initialize empty lists
    middle = []
    std_dev = []
    upper = []
    lower = []
    pctB = []

    for i in range(len(df)):
        if i == 0:
            # Skip first index
            middle.append(None)
            std_dev.append(None)
            upper.append(None)
            lower.append(None)
            pctB.append(None)
            continue

        current_window = min(i + 1, window_size)
        window_data = df['close'].iloc[i - current_window + 1:i + 1]

        mean = window_data.mean()
        std = window_data.std()

        mid = round(mean, 2)
        std_rounded = round(std, 2)
        up = round(mean + (std * 2), 2)
        low = round(mean - (std * 2), 2)

        middle.append(mid)
        std_dev.append(std_rounded)
        upper.append(up)
        lower.append(low)

        # Avoid division by zero
        if up != low:
            pctB_val = (df['close'].iloc[i] - low) / (up - low)
        else:
            pctB_val = 0.5

        pctB.append(pctB_val)

    bollinger_df['STD'] = std_dev
    bollinger_df['Middle'] = middle
    bollinger_df['Upper'] = upper
    bollinger_df['Lower'] = lower
    bollinger_df['%B'] = pctB

    return bollinger_df

def generate_mpf_plot(df, apdict, save_chart=False, pnl=0, trade_n=0):
    fig_kwargs = dict(
        type='candle',
        style='yahoo',
        addplot=apdict,
        figratio=(12, 6),
        figscale=1.2,
        # title=f'Trade {trade_n} | PnL: {pnl}',
        tight_layout=True,
    )

    if save_chart:
        directory = r'D:\Programming\Download_Backtest_Deploy\4__Backtest\ICICI_Backtesting\backtesting_on\output_charts'
        os.makedirs(directory, exist_ok=True)  # <-- Ensures folder is created if missing

        pnl_str = f"{pnl:.2f}"
        fig_kwargs["savefig"] = f'{directory}\\{pnl_str} {trade_n}.png'

    mpf.plot(df, **fig_kwargs)

def plot_chart(df, entry_time, exit_time, entry_price, exit_price, position, pnl, trade_n,
               supertrend_start_time=None,
               plot_bollinger=True, plot_pctb=True, plot_supertrend=False,
               plot_entry_exit=True, save_chart=False):

    df = df.copy()
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    apdict = []

    # Plot Bollinger Bands
    if plot_bollinger:
        apdict += [
            mpf.make_addplot(df['Middle']),
            mpf.make_addplot(df['Upper']),
            mpf.make_addplot(df['Lower'])
        ]

    # Plot %B
    if plot_pctb:
        apdict.append(mpf.make_addplot(
            df['%B'], panel=1, color='g',
            fill_between=dict(y1=0, y2=1, alpha=0.2, interpolate=True, color='olive')
        ))

    def create_signal_df(signal_time, value):
        signal_df = pd.DataFrame(index=df.index)
        signal_df['Signal'] = np.nan
        if signal_time is not None:
            signal_time = pd.to_datetime(signal_time)
            signal_time_index = df.index.indexer_at_time(signal_time.time())
            for idx in signal_time_index:
                signal_df.iloc[idx] = value
        return signal_df

    # Plot Entry/Exit markers
    if plot_entry_exit:
        if entry_time is not None:
            entry_df = create_signal_df(entry_time, entry_price)
            apdict.append(mpf.make_addplot(entry_df['Signal'], type='scatter', markersize=70, secondary_y='auto', color='g'))

        if exit_time is not None:
            exit_df = create_signal_df(exit_time, exit_price)
            apdict.append(mpf.make_addplot(exit_df['Signal'], type='scatter', markersize=70, secondary_y='auto', color='#ab0000'))

    # Plot Supertrend
    if plot_supertrend and supertrend_start_time is not None and exit_time is not None:
        entry_time = pd.to_datetime(entry_time)
        exit_time = pd.to_datetime(exit_time) - pd.Timedelta(minutes=1)
        supertrend_start_time = pd.to_datetime(supertrend_start_time)
        exit_time_adj = exit_time + pd.Timedelta(minutes=2)

        if position == "Short":
            mask = (df.index < entry_time) | (df.index > exit_time_adj)
            df.loc[mask, 'tsl_upperband'] = None
            apdict.append(mpf.make_addplot(df['tsl_upperband'], secondary_y='auto', color='b'))

        elif position == "Long":
            mask = (df.index < supertrend_start_time) | (df.index > exit_time_adj)
            df.loc[mask, 'tsl_lowerband'] = None
            apdict.append(mpf.make_addplot(df['tsl_lowerband'], secondary_y='auto', color='b'))

    generate_mpf_plot(df, apdict, save_chart=save_chart, pnl=pnl, trade_n=trade_n)

def plot_cumulative_return(ddff, output_string, save_file_name, save_fig=False, df_plot_boolian=True):
    if 'pnl' not in ddff.columns:
        print("❌ Error: 'pnl' column not found in ddff.")
        return

    df_plot = ddff.copy()
    df_plot['Cumulative_return'] = df_plot['pnl'].cumsum()

    # Only create and render the plot if at least one condition is true
    if save_fig or df_plot_boolian:
        plt.figure(figsize=(6, 7))
        plt.axhline(0, color='black', linestyle='-')
        df_plot['Cumulative_return'].plot()
        plt.title(output_string)
        plt.xlabel('Time')
        plt.ylabel('Cumulative Return')
        plt.tight_layout()

        # Save if requested
        if save_fig:
            plot_directory = r'Result_charts'
            os.makedirs(plot_directory, exist_ok=True)
            save_path = os.path.join(plot_directory, f"{save_file_name}.png")
            plt.savefig(save_path)
            print(f"✅ Saved plot to: {save_path}")

        # Show if requested
        if df_plot_boolian:
            plt.show()
        else:
            plt.close()  # Close plot if not showing

def calculate_middle_price_change(df, lookback=20):

    df = df.copy()

    df.loc[:, 'Middle_20_pct_change'] = ((df['Middle'] - df['Middle'].shift(lookback)) / df['Middle'].shift(lookback) * 100).round(2)
    df.loc[:, 'ratio'] = df['Middle_20_pct_change'] / (df['STD'] - df['STD'].shift(lookback))
    
    return df

def convert_csv_to_parquet(folder_path):

    # Create parquet folder path
    parquet_folder = os.path.join(folder_path, os.path.basename(folder_path) + '_parquet')

    # Create the parquet directory if it doesn't exist
    os.makedirs(parquet_folder, exist_ok=True)

    # Get list of CSV files
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # Get list of existing parquet files
    existing_parquet = [f[:-8] for f in os.listdir(parquet_folder) if f.endswith('.parquet')]

    # Process only files that don't exist in parquet format
    files_to_convert = [f for f in csv_files if f[:-4] not in existing_parquet]

    if not files_to_convert:
        print("All files already converted to parquet format")
    else:
        print(f"Converting {len(files_to_convert)} files of {os.path.basename(folder_path)} folder to parquet format...")
        
        for file in files_to_convert:
            # Read CSV
            csv_path = os.path.join(folder_path, file)
            parquet_path = os.path.join(parquet_folder, file[:-4] + '.parquet')
            
            print(f"Converting {file}")
            df = pd.read_csv(csv_path)
            
            # Save as parquet
            df.to_parquet(parquet_path)
            
        print("Conversion complete!")

    return parquet_folder
