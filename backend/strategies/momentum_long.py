import numpy as np
from datetime import datetime
from strategies.base import AbstractAlpha

class Alpha(AbstractAlpha):
    def __init__(self):
        super().__init__()
        self.name = 'rotational_alpha_4'
        self.lookback = 1 
        self.factor_list = ['close']
        self.rotation_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        self.base_weights = np.array([0.2, 0.4, 0.6, 0.8], dtype=float)

    def _infer_shift_from_holdings(self, current_pos):
        qtys = np.array([current_pos.get(symbol, 0) for symbol in self.rotation_symbols], dtype=float)
        if np.all(qtys == 0):
            return 0

        max_idx = int(np.argmax(qtys))
        # Highest target-weight symbol by shift:
        # shift 0 -> AMZN, shift 1 -> AAPL, shift 2 -> MSFT, shift 3 -> GOOGL
        max_idx_to_shift = {3: 0, 0: 1, 1: 2, 2: 3}
        return max_idx_to_shift.get(max_idx, 0)

    def generate_day(self, day, data):
        symbols = data.get('symbols', [])
        if not symbols:
            raise ValueError("Strategy input missing 'symbols'.")

        current_pos = data.get('current_positions', {})
        if isinstance(day, int) and day >= 0:
            shift = day % len(self.base_weights)
        else:
            shift = datetime.utcnow().timetuple().tm_yday % len(self.base_weights)
            if current_pos:
                shift = self._infer_shift_from_holdings(current_pos)

        rotated_weights = np.roll(self.base_weights, shift)
        holdings = np.zeros(len(symbols), dtype=float)

        for idx, symbol in enumerate(symbols):
            if symbol in self.rotation_symbols:
                rotation_idx = self.rotation_symbols.index(symbol)
                holdings[idx] = float(rotated_weights[rotation_idx])

        print(f"STATUS: Rotation shift = {shift}")
        print(
            "SIGNAL: "
            + ", ".join(
                f"{s}={holdings[symbols.index(s)]:.2f}" for s in self.rotation_symbols if s in symbols
            )
        )

        return holdings
