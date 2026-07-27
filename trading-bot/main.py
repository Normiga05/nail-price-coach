import argparse
import random
import time

from config import Config
from mexc_client import MexcClientError, get_klines
from paper_broker import PaperBroker
from strategy import LiquidityReversalStrategy


def run_live(cfg: Config) -> None:
    broker = PaperBroker(cfg.starting_balance_usd)
    strategy = LiquidityReversalStrategy(cfg)
    seen_times = set()

    print(f"Paper trading {cfg.symbol} on {cfg.interval} candles. No real orders are ever sent.")
    while True:
        try:
            candles = get_klines(cfg.symbol, cfg.interval, limit=cfg.lookback_candles + 5)
        except MexcClientError as exc:
            print(f"[WARN] MEXC API error, retrying: {exc}")
            time.sleep(cfg.poll_seconds)
            continue

        for candle in candles:
            if candle["time"] in seen_times:
                continue
            seen_times.add(candle["time"])
            strategy.on_candle(candle, broker)

        time.sleep(cfg.poll_seconds)


def run_dry_run(cfg: Config, num_candles: int = 300, seed: int = 7) -> None:
    """Smoke test against synthetic candles - no network needed. Useful to verify
    the strategy/broker logic runs correctly in environments where MEXC is
    unreachable."""
    random.seed(seed)
    broker = PaperBroker(cfg.starting_balance_usd)
    strategy = LiquidityReversalStrategy(cfg)

    price = 25.0
    t = 0
    for _ in range(num_candles):
        o = price
        c = max(0.01, o + random.uniform(-0.4, 0.4))
        h = max(o, c) + random.uniform(0, 0.3)
        lo = min(o, c) - random.uniform(0, 0.3)
        candle = {"time": t, "open": o, "high": h, "low": lo, "close": c, "vol": random.uniform(100, 1000)}
        strategy.on_candle(candle, broker)
        price = c
        t += 300

    print("\n--- Dry-run summary ---")
    for key, value in broker.summary().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MEXC liquidity-sweep reversal paper-trading bot")
    parser.add_argument("--dry-run", action="store_true", help="Run against synthetic candles, no network needed")
    args = parser.parse_args()

    cfg = Config()
    if args.dry_run:
        run_dry_run(cfg)
    else:
        run_live(cfg)
