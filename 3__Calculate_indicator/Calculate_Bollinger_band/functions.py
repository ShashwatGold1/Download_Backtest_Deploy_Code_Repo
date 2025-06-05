import pandas as pd

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
