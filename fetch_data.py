import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ['ALPACA_API_KEY']
API_SECRET = os.environ['ALPACA_API_SECRET']
BASE_URL = 'https://paper-api.alpaca.markets'

headers = {
    'APCA-API-KEY-ID': API_KEY,
    'APCA-API-SECRET-KEY': API_SECRET,
}


def get(path, params=None):
    r = requests.get(f'{BASE_URL}{path}', headers=headers, params=params)
    r.raise_for_status()
    return r.json()


# Account
account = get('/v2/account')

# Portfolio history for each time range
# Alpaca uses "1A" for 1 year
PERIODS = {
    '1D': {'period': '1D', 'timeframe': '5Min'},
    '1M': {'period': '1M', 'timeframe': '1D'},
    '6M': {'period': '6M', 'timeframe': '1D'},
    '1Y': {'period': '1A', 'timeframe': '1D'},
}

history = {}
for label, params in PERIODS.items():
    data = get('/v2/account/portfolio/history', params)
    # Filter out null equity values (e.g. weekends/holidays)
    pairs = [
        (ts, eq)
        for ts, eq in zip(data['timestamp'], data['equity'])
        if eq is not None
    ]
    timestamps, equity = zip(*pairs) if pairs else ([], [])
    history[label] = {
        'timestamps': list(timestamps),
        'equity': list(equity),
    }

# Open positions
positions_raw = get('/v2/positions')
positions = [
    {
        'symbol': p['symbol'],
        'side': p['side'],
        'qty': p['qty'],
        'avg_entry_price': p['avg_entry_price'],
        'current_price': p['current_price'],
        'market_value': p['market_value'],
        'unrealized_pl': p['unrealized_pl'],
        'unrealized_plpc': p['unrealized_plpc'],
    }
    for p in positions_raw
]

# Last 5 filled orders
orders_raw = get('/v2/orders', {'status': 'filled', 'limit': 5, 'direction': 'desc'})
orders = [
    {
        'symbol': o['symbol'],
        'side': o['side'],
        'qty': o.get('filled_qty') or o.get('qty'),
        'type': o['type'],
        'filled_avg_price': o.get('filled_avg_price'),
        'filled_at': o.get('filled_at'),
    }
    for o in orders_raw
]

dashboard = {
    'updated_at': datetime.now(timezone.utc).isoformat(),
    'account': {
        'equity': account['equity'],
        'last_equity': account['last_equity'],
        'buying_power': account['buying_power'],
    },
    'history': history,
    'positions': positions,
    'orders': orders,
}

os.makedirs('data', exist_ok=True)
with open('data/dashboard.json', 'w') as f:
    json.dump(dashboard, f, indent=2)

print(f"Dashboard updated at {dashboard['updated_at']}")
