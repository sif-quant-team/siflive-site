import numpy as np

from sif.siftools.abstractalpha import HoldingsAwareAlpha


class CrossSectionalMeanReversion(HoldingsAwareAlpha):
    name = "cross_sectional_mean_reversion"
    lookback = 15
    universe_size = 2184
    factor_list = ["close", "sector"]
    portfolio_id = 1

    RETURN_WINDOW = 10
    ENTRY_Z = 2.0
    EXIT_Z = 0.5
    MIN_SECTOR_SIZE = 5

    STOP_LOSS_PCT = 0.05
    MAX_POSITION = 0.02
    Z_SCALE = 3.0

    def generate_day(self, day, data, positions):
        close = data["close"]
        sector = data["sector"]

        n = self.universe_size
        weights = np.zeros(n)

        # Measure each stock's recent return against the sector peer group.
        last_price = close[-1]
        start = close[-self.RETURN_WINDOW - 1]
        with np.errstate(invalid="ignore", divide="ignore"):
            returns = np.where(start != 0, (last_price - start) / start, np.nan)

        returns[last_price < self.MIN_STOCK_PRICE] = np.nan

        # Convert relative sector returns into z-scores.
        sectors = sector[-1]
        z_scores = np.full(n, np.nan)

        for sec in set(s for s in sectors if isinstance(s, str) and s):
            mask = sectors == sec
            peer_returns = returns[mask]
            valid = peer_returns[np.isfinite(peer_returns)]
            if len(valid) < self.MIN_SECTOR_SIZE:
                continue

            sigma = valid.std()
            if sigma == 0:
                continue

            z_scores[mask] = np.where(
                np.isfinite(peer_returns),
                (peer_returns - valid.mean()) / sigma,
                np.nan,
            )

        tickers = getattr(self, "_universe_tickers", [None] * n)

        for i, z in enumerate(z_scores):
            if not np.isfinite(z):
                continue

            ticker = tickers[i] if i < len(tickers) else None
            position = positions.get(ticker) if ticker else None

            if position is None:
                if z > self.ENTRY_Z:
                    weights[i] = max(-(z / self.Z_SCALE), -self.MAX_POSITION)
                elif z < -self.ENTRY_Z:
                    weights[i] = min(abs(z) / self.Z_SCALE, self.MAX_POSITION)
                continue

            position_value = abs(float(position.value))
            pnl_pct = position.gain / position_value if position_value else 0

            if pnl_pct < -self.STOP_LOSS_PCT:
                weights[i] = 0
            elif position.side == "short" and z >= self.EXIT_Z:
                weights[i] = max(-(z / self.Z_SCALE), -self.MAX_POSITION)
            elif position.side == "long" and z <= -self.EXIT_Z:
                weights[i] = min(abs(z) / self.Z_SCALE, self.MAX_POSITION)

        # Keep long and short exposure balanced.
        long_total = weights[weights > 0].sum()
        short_total = abs(weights[weights < 0].sum())

        if long_total > 0 and short_total > 0:
            if long_total > short_total:
                weights[weights > 0] *= short_total / long_total
            else:
                weights[weights < 0] *= long_total / short_total

        total_exposure = np.abs(weights).sum()
        if total_exposure > 1.0:
            weights /= total_exposure

        return weights
