from datetime import datetime, timezone
from sqlalchemy import select
from .db import SessionLocal
from .models import EquityPoint, Fill
from . import alpaca

def upsert_equity_points():
    data = alpaca.portfolio_history(period="all", timeframe="1D")
    # data like: { "timestamp":[...seconds...], "equity":[...], "profit_loss":[...], "profit_loss_pct":[...] }
    stamps = data.get("timestamp", [])
    equities = data.get("equity", [])
    pnls = data.get("profit_loss", [])
    pnl_pcts = data.get("profit_loss_pct", [])
    with SessionLocal() as s:
        for i, sec in enumerate(stamps):
            row = s.get(EquityPoint, alpaca.ms(sec))
            if not row:
                row = EquityPoint(
                    ts=alpaca.ms(sec),
                    equity=float(equities[i]),
                    pnl=float(pnls[i]) if i < len(pnls) and pnls[i] is not None else None,
                    pnl_pct=float(pnl_pcts[i]) if i < len(pnl_pcts) and pnl_pcts[i] is not None else None,
                )
                s.add(row)
            else:
                row.equity = float(equities[i])
                if i < len(pnls) and pnls[i] is not None: row.pnl = float(pnls[i])
                if i < len(pnl_pcts) and pnl_pcts[i] is not None: row.pnl_pct = float(pnl_pcts[i])
        s.commit()

def isoformat_ms(ms_val: int) -> str:
    return datetime.fromtimestamp(ms_val/1000, tz=timezone.utc).isoformat()

def ingest_new_fills():
    with SessionLocal() as s:
        # get latest fill ts to use 'after'
        last_ts = s.execute(select(Fill.ts).order_by(Fill.ts.desc())).scalars().first()
        after_iso = isoformat_ms(last_ts) if last_ts else None

        for f in alpaca.iter_fills(after_iso=after_iso):
            # f sample keys: 'id','symbol','side','qty','price','transaction_time','order_id'
            fid = f["id"]
            if s.get(Fill, fid):
                continue
            ts = datetime.fromisoformat(f["transaction_time"].replace("Z","+00:00")).timestamp()
            fill = Fill(
                id=fid,
                ts=alpaca.ms(ts),
                symbol=f["symbol"],
                side=f["side"].lower(),
                qty=float(f["qty"]),
                price=float(f["price"]),
                order_id=f.get("order_id")
            )
            s.add(fill)
        s.commit()

def run_ingest_once():
    upsert_equity_points()
    ingest_new_fills()
