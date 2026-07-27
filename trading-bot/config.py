from dataclasses import dataclass


@dataclass
class Config:
    symbol: str = "HYPE_USDT"
    interval: str = "Min5"

    # --- Liquidity pool detection (ASSUMPTION - validate against the real strategy) ---
    # A "pool" is either 2+ highs/lows sitting within tolerance of each other (equal
    # highs/lows) or a round-number level. Neither definition has been confirmed by
    # the person who actually trades this strategy - treat these as a first draft.
    lookback_candles: int = 50
    equal_level_tolerance_pct: float = 0.05

    # Spacing between round-number levels. The strategy was described in terms of
    # 50/100 round levels for a BTC-scale asset - HYPE trades far lower, so adjust
    # this to match HYPE's actual price range before relying on it.
    round_number_step: float = 1.0
    round_number_span: int = 5

    # --- Trade management ---
    stop_loss_pct: float = 1.0
    max_hold_candles: int = 8

    # --- Martingale doubling (high risk - kept small on purpose) ---
    martingale_max_doubles: int = 1
    martingale_multiplier: float = 2.0
    martingale_watch_candles: int = 8

    # --- Paper trading (simulated, no real orders) ---
    starting_balance_usd: float = 1000.0
    risk_per_trade_usd: float = 20.0
    poll_seconds: int = 30
