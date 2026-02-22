import math
import time

class TradingEngine:
    def __init__(self, client):
        self.client = client

    def _execute_orders(self, orders):
        sells = [o for o in orders if o['side'] == 'sell']
        buys = [o for o in orders if o['side'] == 'buy']

        print(f"\n[EXECUTION] Processing {len(sells)} sells and {len(buys)} buys...")
        for o in sells:
            self._submit(o)
        if sells and buys:
            time.sleep(1)
        for o in buys:
            self._submit(o)

    def rebalance(self, target_weights, symbols, total_equity):
        if len(target_weights) != len(symbols):
            raise ValueError(
                f"Length mismatch: got {len(target_weights)} weights for {len(symbols)} symbols."
            )

        _, current_positions = self.client.get_account_state()
        orders = []

        # Cleanup positions not in the universe
        for symbol, qty in current_positions.items():
            if symbol not in symbols and qty != 0:
                orders.append({'symbol': symbol, 'qty': abs(qty), 'side': 'sell' if qty > 0 else 'buy'})

        # Calculate adjustments for universe
        for i, symbol in enumerate(symbols):
            weight = float(target_weights[i])
            if weight < 0:
                raise ValueError(f"Negative target weight for {symbol}: {weight}")
            try:
                price = self.client.api.get_latest_trade(symbol).price
            except Exception as exc:
                raise RuntimeError(f"Failed to fetch latest price for {symbol}: {exc}") from exc

            target_qty = math.floor((weight * total_equity) / price)
            diff = target_qty - current_positions.get(symbol, 0)
            if diff != 0:
                orders.append({'symbol': symbol, 'qty': abs(diff), 'side': 'buy' if diff > 0 else 'sell'})

        self._execute_orders(orders)

    def rebalance_to_shares(self, target_shares, symbols):
        _, current_positions = self.client.get_account_state()
        orders = []

        for symbol, qty in current_positions.items():
            if symbol not in symbols and qty != 0:
                orders.append({'symbol': symbol, 'qty': abs(qty), 'side': 'sell' if qty > 0 else 'buy'})

        for symbol in symbols:
            target_qty = int(target_shares.get(symbol, 0))
            if target_qty < 0:
                raise ValueError(f"Negative target shares for {symbol}: {target_qty}")
            diff = target_qty - current_positions.get(symbol, 0)
            if diff != 0:
                orders.append({'symbol': symbol, 'qty': abs(diff), 'side': 'buy' if diff > 0 else 'sell'})

        self._execute_orders(orders)

    def _submit(self, order):
        print(f"  - {order['side'].upper()} {order['qty']} {order['symbol']}")
        if order['qty'] <= 0:
            return
        self.client.api.submit_order(symbol=order['symbol'], qty=order['qty'], side=order['side'], type='market', time_in_force='day')
        time.sleep(0.5)
