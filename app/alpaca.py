import os, time
import httpx
from dotenv import load_dotenv

load_dotenv()  # ensure .env is loaded even if main didn't

def _get_env(name: str, *, required: bool = True, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if required and not val:
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            "Set it in your .env or host env (no quotes)."
        )
    return val

def _client() -> httpx.Client:
    apca_key   = _get_env("APCA_API_KEY_ID")
    apca_secret= _get_env("APCA_API_SECRET_KEY")
    base_url   = _get_env("APCA_BASE_URL", required=False, default="https://paper-api.alpaca.markets")
    headers = {
        "APCA-API-KEY-ID": apca_key,
        "APCA-API-SECRET-KEY": apca_secret,
    }
    return httpx.Client(base_url=base_url, headers=headers, timeout=30.0)

def portfolio_history(period="all", timeframe="1D"):
    with _client() as c:
        r = c.get("/v2/account/portfolio/history", params={"period": period, "timeframe": timeframe})
        r.raise_for_status()
        return r.json()

def iter_fills(after_iso: str | None = None):
    params = {"activity_types": "FILL", "page_size": 100}
    if after_iso:
        params["after"] = after_iso  # RFC3339
    url = "/v2/account/activities"
    with _client() as c:
        while True:
            r = c.get(url, params=params)
            r.raise_for_status()
            items = r.json()
            if not items:
                break
            for it in items:
                yield it
            cursor = r.headers.get("x-next-page-token")
            if not cursor:
                break
            params["page_token"] = cursor

def ms(ts_seconds: int | float) -> int:
    return int(round(float(ts_seconds) * 1000))
