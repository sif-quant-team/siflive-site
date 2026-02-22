import alpaca_trade_api as tradeapi
import pandas as pd

class AlpacaClient:
    def __init__(self, key, secret, url):
        self.api = tradeapi.REST(key, secret, url)

    def get_historical_data(self, symbols, lookback):
        try:
            bars = self.api.get_bars(symbols, '1Day', limit=lookback * len(symbols), feed='iex').df
            if bars.empty: return pd.DataFrame()
            if 'symbol' not in bars.columns: bars = bars.reset_index()
            return bars.pivot(index='timestamp', columns='symbol', values='close')
        except Exception as e:
            print(f"Data Fetch Error: {e}")
            return pd.DataFrame()

    def get_account_state(self):
        account = self.api.get_account()
        positions = self.api.list_positions()
        pos_dict = {p.symbol: int(p.qty) for p in positions}
        return float(account.equity), pos_dict

    def get_raw_positions(self):
        return self.api.list_positions()