import nest_asyncio
import ast
from dhanhq import dhanhq, DhanContext, MarketFeed
import functions as f

# Your existing code to get credentials
client_id = str(ast.literal_eval(f.get_line(r'D:\Programming\Download_Backtest_Deploy\5__Deploy\Multi_deploy\data\database.txt', 3).strip())['client_id'])
access_token = str(ast.literal_eval(f.get_line(r'D:\Programming\Download_Backtest_Deploy\5__Deploy\Multi_deploy\data\database.txt', 4).strip())['access_token'])

# Correct v2.1.0 initialization
dhan_context = DhanContext(client_id, access_token)
dhan = dhanhq(dhan_context)


# Enable nested event loops for Jupyter
nest_asyncio.apply()

# Structure for subscribing is (exchange_segment, "security_id", subscription_type)

instruments = [(MarketFeed.NSE, "1333", MarketFeed.Ticker)]

version = "v2"          # Mention Version and set to latest version 'v2'

# In case subscription_type is left as blank, by default Ticker mode will be subscribed.

try:
    data = MarketFeed(dhan_context, instruments, version)
    
    while True:
        data.run_forever()
        response = data.get_data()
        print(response)

except Exception as e:
    print("Error", e)
