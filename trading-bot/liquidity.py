from dataclasses import dataclass


@dataclass
class LiquidityLevel:
    price: float
    kind: str  # "resistance" (pool above price, shorts trigger here) or "support" (below, longs trigger here)
    source: str  # "equal_level" or "round_number"


def find_equal_levels(candles: list[dict], lookback: int, tolerance_pct: float) -> list[LiquidityLevel]:
    """Group recent highs/lows sitting within tolerance_pct of each other.

    Two or more touches at (roughly) the same price is treated as a liquidity
    pool - this is a first-draft definition of "equal highs/lows", not a
    confirmed rule from the person who trades this strategy manually.
    """
    recent = candles[-lookback:]
    levels: list[LiquidityLevel] = []
    _cluster(recent, "high", "resistance", tolerance_pct, levels)
    _cluster(recent, "low", "support", tolerance_pct, levels)
    return levels


def _cluster(recent, field, kind, tolerance_pct, levels):
    prices = sorted(c[field] for c in recent)
    used = [False] * len(prices)
    for i, p in enumerate(prices):
        if used[i]:
            continue
        group = [p]
        used[i] = True
        for j in range(i + 1, len(prices)):
            if used[j]:
                continue
            if abs(prices[j] - p) / p <= tolerance_pct / 100:
                group.append(prices[j])
                used[j] = True
        if len(group) >= 2:
            levels.append(LiquidityLevel(price=sum(group) / len(group), kind=kind, source="equal_level"))


def round_number_levels(price: float, step: float, span: int) -> list[LiquidityLevel]:
    """Round levels above/below the current price, spaced by `step`, out to `span` steps each side."""
    base = round(price / step) * step
    levels = []
    for n in range(-span, span + 1):
        if n == 0:
            continue
        lvl = base + n * step
        kind = "resistance" if lvl > price else "support"
        levels.append(LiquidityLevel(price=lvl, kind=kind, source="round_number"))
    return levels


def detect_sweep(candle: dict, level: LiquidityLevel) -> bool:
    """A pool is "eaten"/completed when a wick pierces it but the candle closes
    back inside the range - a sweep followed by rejection."""
    if level.kind == "resistance":
        return candle["high"] > level.price and candle["close"] < level.price
    return candle["low"] < level.price and candle["close"] > level.price
