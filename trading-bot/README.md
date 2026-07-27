# MEXC Liquidity-Sweep Reversal Bot (Paper Trading)

Simulated bot for a discretionary reversal strategy on MEXC futures (5-minute
candles): wait for a liquidity pool to be fully swept, then enter counter-trend.

**This bot never places real orders.** MEXC's API does not expose a
sandbox/testnet for its own "Demo Trading" feature (it only connects to the
live trading environment), so instead this project pulls MEXC's public
market-data endpoints (no API key or KYC required) and simulates fills, stop
losses, and P&L locally in `paper_broker.py`.

## Strategy as described (first draft - needs validation)

- Timeframe: 5-minute candles, symbol `HYPE_USDT` by default.
- Entry: reversal (short/long) when a liquidity pool is "eaten" - a wick
  pierces the level and the candle closes back inside the range.
- Stop loss: ~1% from entry (configurable), placed at the swept level.
- Max hold: 8 candles, otherwise closed at market.
- Runs continuously, no session/time-of-day filter.
- After a stop-out, optionally doubles into the next round-number pool in the
  same continuation direction (martingale, capped at `martingale_max_doubles`).

**"Liquidity pool" and "sweep" are judgment calls the actual trader (not this
bot) makes visually.** The code encodes one reasonable guess at a mechanical
definition:

- `equal_level`: 2+ recent highs (or lows) within `equal_level_tolerance_pct`
  of each other - see `liquidity.find_equal_levels`.
- `round_number`: price levels spaced by `round_number_step` - see
  `liquidity.round_number_levels`. The original description used 50/100 as
  round levels for a BTC-scale asset; **adjust `round_number_step` in
  `config.py` for HYPE's actual price range** before trusting this.

Before this is used for anything beyond observation, have the person who
trades this manually watch the bot's signals next to their own chart and
confirm the pools/sweeps match what they'd flag by eye.

## Running it

```bash
pip install -r requirements.txt

# Smoke test with synthetic candles - no network required
python main.py --dry-run

# Poll real MEXC market data and paper-trade against it
python main.py
```

Live mode logs every simulated open/close and running virtual balance to
stdout - nothing is persisted or sent to a broker.

## Known limitation

This was built in a sandbox whose network policy blocks `contract.mexc.com`,
so the live-data path (`mexc_client.py`) is implemented against MEXC's
documented contract-kline response shape but has not been exercised against
the real API. Run `python main.py` somewhere with network access to MEXC and
report back any request/parsing errors - the response format is the most
likely thing to need a small fix.

## Configuration

All knobs live in `config.py`: symbol, candle interval, pool-detection
tolerance, round-number spacing, stop-loss %, max hold, and the martingale
settings. Nothing here is tuned/backtested - these are starting defaults.

## Path to live trading (not built yet, deliberately)

Once the paper-trading signals are validated: MEXC Futures API order
placement requires KYC-verified API keys with Futures trading permission.
That's a separate, explicit step - real money execution should only be wired
up after the detection logic above is confirmed against the manual strategy,
and ideally after reviewing a run of paper-trading results together.
