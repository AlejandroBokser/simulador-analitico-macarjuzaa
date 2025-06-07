import pandas as pd

df = pd.read_csv('btcdata.csv', parse_dates=['Time'])
df['date'] = df['Time'].dt.floor('D')
# Use last price of each day
daily = df.groupby('date')['BTC'].last().reset_index()

daily['ma180'] = daily['BTC'].rolling(window=180, min_periods=1).mean()
ma180_df = daily[['date','ma180']]
ma180_df.to_csv('btc_ma180.csv', index=False)
print('Generado: btc_ma180.csv')
