import time

import requests

BASE_URL = "https://contract.mexc.com"

_INTERVAL_SECONDS = {
    "Min1": 60,
    "Min5": 300,
    "Min15": 900,
    "Min30": 1800,
    "Min60": 3600,
    "Hour4": 14400,
    "Hour8": 28800,
    "Day1": 86400,
}


class MexcClientError(Exception):
    pass


def get_klines(symbol: str, interval: str = "Min5", limit: int = 200) -> list[dict]:
    """Fetch recent candles for a MEXC futures contract.

    MEXC's contract kline endpoint returns parallel arrays (time/open/high/low/
    close/vol) under "data" rather than a list of rows - the parsing below
    depends on that shape holding.
    """
    if interval not in _INTERVAL_SECONDS:
        raise ValueError(f"Unsupported interval: {interval}")

    end = int(time.time())
    start = end - limit * _INTERVAL_SECONDS[interval]
    url = f"{BASE_URL}/api/v1/contract/kline/{symbol}"
    resp = requests.get(url, params={"interval": interval, "start": start, "end": end}, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("success"):
        raise MexcClientError(f"MEXC API error: {payload}")

    data = payload["data"]
    candles = [
        {"time": t, "open": o, "high": h, "low": lo, "close": c, "vol": v}
        for t, o, h, lo, c, v in zip(
            data["time"], data["open"], data["high"], data["low"], data["close"], data["vol"]
        )
    ]
    return candles


def get_last_price(symbol: str) -> float:
    url = f"{BASE_URL}/api/v1/contract/ticker"
    resp = requests.get(url, params={"symbol": symbol}, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("success"):
        raise MexcClientError(f"MEXC API error: {payload}")
    return float(payload["data"]["lastPrice"])
