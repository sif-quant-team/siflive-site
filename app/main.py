from dotenv import load_dotenv; load_dotenv()
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from .db import init_db, SessionLocal
from .models import EquityPoint, Fill
from .ingest import run_ingest_once

POLL_MINUTES = int(os.getenv("POLL_MINUTES", "5"))

app = FastAPI(title="Alpaca PnL API")

# Allow any origin for now; you can tighten later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"],
)

scheduler = BackgroundScheduler()

@app.on_event("startup")
def on_startup():
    init_db()
    run_ingest_once()  # prime data on boot
    scheduler.start()
    scheduler.add_job(run_ingest_once, IntervalTrigger(minutes=POLL_MINUTES), id="poll-alpaca", replace_existing=True)

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown(wait=False)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/equity")
def get_equity():
    with SessionLocal() as s:
        rows = s.execute(select(EquityPoint).order_by(EquityPoint.ts)).scalars().all()
        points = [[r.ts, r.equity] for r in rows]
        return {"points": points, "count": len(points)}

@app.get("/api/fills")
def get_fills(limit: int = 200):
    limit = max(1, min(limit, 2000))
    with SessionLocal() as s:
        rows = s.execute(select(Fill).order_by(Fill.ts.desc()).limit(limit)).scalars().all()
        out = [
            {
                "id": r.id, "ts": r.ts, "symbol": r.symbol,
                "side": r.side, "qty": r.qty, "price": r.price,
                "order_id": r.order_id,
            } for r in rows
        ]
        return {"fills": out, "count": len(out)}
