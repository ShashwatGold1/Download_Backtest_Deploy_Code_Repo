
import ast
from dhanhq import dhanhq, DhanContext
import functions as f
import pandas as pd
from datetime import datetime
import time
from config import MYPATHS


def run_master_list_to_option_chain():

    database_path = MYPATHS['data'] + "\\database.txt"
    line = ast.literal_eval(f.get_line(database_path, 2).strip())
    master_list_date = line['master_list_date'] 

    today = datetime.now().date()
    today_date = f'{today.day}-{today.month}-{today.year}'

    if master_list_date != today_date:

        if not datetime.now().time() < datetime.strptime("09:10:00", "%H:%M:%S").time():
            f.play_sound(file_name = "Alert_01", error_message = "You missed today’s market — All because you were late.", raise_error = True)

        client_id = str(ast.literal_eval(f.get_line(database_path, 3).strip())['client_id'])
        access_token = str(ast.literal_eval(f.get_line(database_path, 4).strip())['access_token'])

        # Correct v2.1.0 initialization
        dhan_context = DhanContext(client_id, access_token)
        dhan = dhanhq(dhan_context)

        def get_latest_expiry(nifty_security_id, nifty_exchange_segment):

            # Get latest Nifty expiry
            nifty_expiry_list = dhan.expiry_list(nifty_security_id, nifty_exchange_segment)
            latest_expiry = nifty_expiry_list['data']['data'][0]

            # Convert to datetime and extract components
            expiry_date = datetime.strptime(latest_expiry, '%Y-%m-%d')

            month = expiry_date.strftime('%b').upper()  # 3-letter month in caps

            return latest_expiry, month

        latest_expiry, month = get_latest_expiry(13, "IDX_I") # 13 NIFTY security_id
        latest_expiry, month

        master_list = pd.read_csv("https://images.dhan.co/api-data/api-scrip-master.csv", sep=None, engine='python', on_bad_lines='skip')

        master_12 = master_list.copy()
        master_12[["symbol1", "date1", "month1", "strike1", "CE_PE1"]] = master_12["SEM_CUSTOM_SYMBOL"].str.split(" ", n=4, expand=True)
        master_12 = master_12[master_12['strike1'].apply(lambda x: str(x).isnumeric())]
        master_12['strike1'] = pd.to_numeric(master_12['strike1'])
        master_12 = master_12[['SEM_EXM_EXCH_ID', 'SEM_INSTRUMENT_NAME', 'symbol1', 'month1', 'date1', 'strike1', 'SEM_CUSTOM_SYMBOL', 'SEM_SMST_SECURITY_ID', 'CE_PE1']]

        master_12 = master_12[
            (master_12.date1 == latest_expiry[-2:]) &
            (master_12.month1 == month) &
            (master_12.SEM_INSTRUMENT_NAME == "OPTIDX") &
            (master_12.symbol1 == "NIFTY")]

        master_12.to_csv(MYPATHS['data'] + "\\master_list.csv", index=False)
        f.update_line(database_path, 2, {'master_list_date': today_date})

        # =================== Get Option Chain from Dhan and convert to Dataframe ===================

        master_12 = pd.read_csv(MYPATHS['data'] + "\\master_list.csv")

        responce = dhan.option_chain(
            under_security_id=13,                       # Nifty
            under_exchange_segment="IDX_I",
            expiry=latest_expiry
        )

        def extract_option_chain_data(response_json):
            oc_data = response_json['data']['data']['oc']
            rows = []

            for strike, data in oc_data.items():
                ce = data.get('ce', {})
                pe = data.get('pe', {})

                row = {
                    'strike_price': float(strike),
                    'ce_iv': ce.get('implied_volatility', 0),
                    'ce_last_price': ce.get('last_price', 0),
                    'ce_oi': ce.get('oi', 0),
                    'ce_volume': ce.get('volume', 0),
                    'pe_iv': pe.get('implied_volatility', 0),
                    'pe_last_price': pe.get('last_price', 0),
                    'pe_oi': pe.get('oi', 0),
                    'pe_volume': pe.get('volume', 0)
                }
                rows.append(row)

            df = pd.DataFrame(rows)
            df.sort_values('strike_price', inplace=True)
            df = df[['ce_iv', 'ce_volume', 'ce_oi', 'ce_last_price', 'strike_price', 'pe_last_price', 'pe_iv', 'pe_oi', 'pe_volume']]

            df = df[(df['ce_last_price'] != 0.0) & (df['pe_last_price'] != 0.0)]
            df.reset_index(drop=True, inplace=True)

            df.insert(0, 'security_id_CE', None)
            df['security_id_PE'] = None

            return df

        df = extract_option_chain_data(responce)

        # =================== Add security id ===================

        for i in range(0, len(df)):
            # print(i, int(df['strike_price'].iloc[i]))

            mask_CE = (master_12['strike1'].values == int(df['strike_price'].iloc[i])) & (master_12['CE_PE1'].values == 'CALL')
            filtered_ids_CE = master_12['SEM_SMST_SECURITY_ID'].values[mask_CE]
            sem_smst_security_id_CE = filtered_ids_CE[0] if filtered_ids_CE.size > 0 else None

            df.loc[i, 'security_id_CE'] = sem_smst_security_id_CE

            # -------------------------------------

            mask_PE = (master_12['strike1'].values == int(df['strike_price'].iloc[i])) & (master_12['CE_PE1'].values == 'PUT')
            filtered_ids_PE = master_12['SEM_SMST_SECURITY_ID'].values[mask_PE]
            sem_smst_security_id_PE = filtered_ids_PE[0] if filtered_ids_PE.size > 0 else None

            df.loc[i, 'security_id_PE'] = sem_smst_security_id_PE

        # =================== Save option Chain with Security id ===================

        today_date = datetime.now().strftime('%Y-%m-%d')
        file_path = MYPATHS['Option_Chain_with_Security_id'] + f"\\{today_date}.csv"

        df.to_csv(file_path, index=False)

        df

