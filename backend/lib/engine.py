import math
import time

class TradingEngine:
    def __init__(self, client):
        self.client = client

    def rebalance(self, target_weights, symbols, total_equity):
        _, current_positions = self.client.get_account_state()
        orders = []

        # Cleanup positions not in the universe
        for symbol, qty in current_positions.items():
            if symbol not in symbols and qty != 0:
                orders.append({'symbol': symbol, 'qty': abs(qty), 'side': 'sell' if qty > 0 else 'buy'})

        # Calculate adjustments for universe
        for i, symbol in enumerate(symbols):
            weight = target_weights[i]
            try:
                price = self.client.api.get_latest_trade(symbol).price
            except:
                continue

            target_qty = math.floor((weight * total_equity) / price)
            diff = target_qty - current_positions.get(symbol, 0)
            if diff != 0:
                orders.append({'symbol': symbol, 'qty': abs(diff), 'side': 'buy' if diff > 0 else 'sell'})

        sells = [o for o in orders if o['side'] == 'sell']
        buys = [o for o in orders if o['side'] == 'buy']

        print(f"\n[EXECUTION] Processing {len(sells)} sells and {len(buys)} buys...")
        for o in sells: self._submit(o)
        if sells and buys: time.sleep(1)
        for o in buys: self._submit(o)

    def _submit(self, order):
        print(f"  - {order['side'].upper()} {order['qty']} {order['symbol']}")
        self.client.api.submit_order(symbol=order['symbol'], qty=order['qty'], side=order['side'], type='market', time_in_force='day')
        time.sleep(0.5)