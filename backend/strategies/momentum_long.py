import numpy as np
from strategies.base import AbstractAlpha

class Alpha(AbstractAlpha):
    def __init__(self):
        super().__init__()
        self.name = 'flip_aapl_msft'
        self.lookback = 1 
        self.factor_list = ['close']

    def generate_day(self, day, data):
        """
        Flips weights based on current holdings:
        - If AAPL > MSFT: Target 25% AAPL / 75% MSFT
        - If MSFT >= AAPL: Target 75% AAPL / 25% MSFT
        """
        num_stocks = data['close'].shape[1]
        holdings = np.zeros(num_stocks)

        # Indices based on UNIVERSE order in config.py
        aapl_idx = 0
        msft_idx = 1

        # Extract current positions passed from main.py
        current_pos = data.get('current_positions', {})
        
        aapl_qty = current_pos.get('AAPL', 0)
        msft_qty = current_pos.get('MSFT', 0)

        # Decision Logic
        if aapl_qty > msft_qty:
            holdings[aapl_idx] = 0.25
            holdings[msft_idx] = 0.75
            print(f"STATUS: Currently AAPL Heavy ({aapl_qty} shares).")
            print("SIGNAL: Flipping to 25% AAPL / 75% MSFT.")
        else:
            holdings[aapl_idx] = 0.75
            holdings[msft_idx] = 0.25
            print(f"STATUS: Currently MSFT Heavy or Empty ({msft_qty} shares).")
            print("SIGNAL: Flipping to 75% AAPL / 25% MSFT.")

        return holdings