import alpaca_trade_api as tradeapi
import config

print("--- ALPACA AUTH DIAGNOSTIC ---")
# 1. Verify what the script actually "sees"
print(f"Base URL: {config.BASE_URL}")
print(f"API Key present: {bool(config.API_KEY)}")
print(f"Secret Key present: {bool(config.SECRET_KEY)}")

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, config.BASE_URL)

print("\nStep 1: Testing Account Access (Trading API)...")
try:
    acc = api.get_account()
    print(f"SUCCESS: Connected to Account ID {acc.id}")
    print(f"Account Status: {acc.status}")
except Exception as e:
    print(f"FAILED Account Access: {e}")

print("\nStep 2: Testing Market Data Access (Data API)...")
try:
    # Testing with a single bar and explicit IEX feed
    bar = api.get_bars("AAPL", "1Day", limit=1, feed='iex')
    print("SUCCESS: Retrieved Market Data")
except Exception as e:
    print(f"FAILED Data Access: {e}")
