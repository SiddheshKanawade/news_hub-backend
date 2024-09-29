import requests
import pandas as pd
import io

nse_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

# create Session from 'real' browser
headers = {
    'User-Agent': 'Mozilla/5.0'
}

s = requests.Session()
s.headers.update(headers)

# do a get call now
url = 'https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv'
r = s.get(nse_url)
s.close()

# saving it to pd df for further preprocessing
df_nse = pd.read_csv(io.BytesIO(r.content))
df_nse.to_csv('../static/nse.csv')