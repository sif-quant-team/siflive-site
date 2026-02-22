import json
import os
from datetime import datetime
from lib.alpaca_client import AlpacaClient
from lib.engine import TradingEngine
from strategies.momentum_long import Alpha
import config

def print_portfolio_status(equity, raw_positions):
    print("\n" + "="*50)
    print(f" CURRENT PORTFOLIO STATUS | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    print(f" Total Equity: ${equity:,.2f}")
    print("-" * 50)
    print(f"{'SYMBOL':<10} | {'QTY':<8} | {'MARKET VALUE':<15} | {'PL %':<10}")
    print("-" * 50)
    
    if not raw_positions:
        print(" No open positions.")
    else:
        for p in raw_positions:
            pl_pc = float(p.unrealized_plpc) * 100
            print(f"{p.symbol:<10} | {p.qty:<8} | ${float(p.market_value):<14,.2f} | {pl_pc:>8.2f}%")
    print("="*50)

def update_dashboard_file(equity, positions):
    data = {"total_equity": equity, "holdings": positions, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    path = os.path.join(os.path.dirname(__file__), '../data/dashboard.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    client = AlpacaClient(config.API_KEY, config.SECRET_KEY, config.BASE_URL)
    engine = TradingEngine(client)
    strategy = Alpha()

    # 1. Show Current Status
    equity, current_pos_dict = client.get_account_state()
    raw_positions = client.get_raw_positions()
    print_portfolio_status(equity, raw_positions)

    # 2. Get Strategy Signal
    df = client.get_historical_data(config.UNIVERSE, strategy.lookback)
    df = df.reindex(columns=config.UNIVERSE).fillna(0)
    data_dict = {'close': df.values, 'current_positions': current_pos_dict}
    weights = strategy.generate_day(-1, data_dict)

    # 3. Interactive Confirmation
    choice = input("\nDo you want to execute this Alpha's rebalance? (y/n): ").lower().strip()
    
    if choice == 'y':
        engine.rebalance(weights, config.UNIVERSE, equity)
        # Update state after trades
        new_equity, new_pos = client.get_account_state()
        update_dashboard_file(new_equity, new_pos)
        print("\nRebalance complete. Dashboard updated.")
    else:
        print("\nExecution cancelled by user. No trades were made.")

if __name__ == "__main__":
    main()