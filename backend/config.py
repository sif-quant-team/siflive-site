import os
from dotenv import load_dotenv

# Load variables from backend/.env
load_dotenv()

# Syncing with your frontend naming convention
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_API_SECRET')
BASE_URL = 'https://paper-api.alpaca.markets'

# Universe order: AAPL (Index 0), MSFT (Index 1)
UNIVERSE = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK.B", "JNJ", "V"] 
LEVERAGE = 1.0