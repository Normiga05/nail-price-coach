from dataclasses import dataclass
from typing import Optional

from liquidity import LiquidityLevel, detect_sweep, find_equal_levels, round_number_levels


@dataclass
class Position:
    direction: str  # "long" or "short"
    entry_price: float
    size_usd: float
    stop_price: float
    opened_at_index: int
    doubles_used: int = 0


@dataclass
class PendingDouble:
    target_level: LiquidityLevel
    doubles_used: int
    expires_at_index: int


class LiquidityReversalStrategy:
    """Reversal-on-sweep strategy: waits for a liquidity pool (equal highs/lows
    or a round-number level) to be swept, then enters counter-trend. On a
    stop-out, optionally waits for the next round-number pool in the same
    continuation direction and doubles in in reversal there (capped by
    martingale_max_doubles)."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.position: Optional[Position] = None
        self.pending_double: Optional[PendingDouble] = None
        self.candles: list[dict] = []

    def on_candle(self, candle: dict, broker) -> None:
        self.candles.append(candle)
        idx = len(self.candles) - 1

        if self.position is not None:
            self._manage_position(candle, idx, broker)
            return

        if self.pending_double is not None:
            self._check_pending_double(candle, idx, broker)
            return

        levels = find_equal_levels(self.candles, self.cfg.lookback_candles, self.cfg.equal_level_tolerance_pct)
        levels += round_number_levels(candle["close"], self.cfg.round_number_step, self.cfg.round_number_span)

        for level in levels:
            if detect_sweep(candle, level):
                self._open_position(level, candle, idx, broker)
                break

    def _open_position(self, level, candle, idx, broker, doubles_used=0, size_multiplier=1.0):
        direction = "short" if level.kind == "resistance" else "long"
        entry = candle["close"]
        sl_distance = entry * self.cfg.stop_loss_pct / 100
        stop_price = entry - sl_distance if direction == "long" else entry + sl_distance
        size_usd = self.cfg.risk_per_trade_usd * size_multiplier
        self.position = Position(direction, entry, size_usd, stop_price, idx, doubles_used)
        broker.open(direction, entry, size_usd)

    def _manage_position(self, candle, idx, broker):
        pos = self.position
        hit_stop = (
            candle["low"] <= pos.stop_price
            if pos.direction == "long"
            else candle["high"] >= pos.stop_price
        )
        timed_out = (idx - pos.opened_at_index) >= self.cfg.max_hold_candles

        if hit_stop:
            broker.close(pos.direction, pos.stop_price, pos.size_usd, reason="stop_loss")
            self.position = None
            self._arm_pending_double(candle, idx, pos)
        elif timed_out:
            broker.close(pos.direction, candle["close"], pos.size_usd, reason="timeout")
            self.position = None

    def _arm_pending_double(self, candle, idx, closed_pos):
        if closed_pos.doubles_used >= self.cfg.martingale_max_doubles:
            return
        next_levels = round_number_levels(candle["close"], self.cfg.round_number_step, self.cfg.round_number_span)
        continuation_kind = "resistance" if closed_pos.direction == "short" else "support"
        candidates = [lvl for lvl in next_levels if lvl.kind == continuation_kind]
        if not candidates:
            return
        nearest = min(candidates, key=lambda lvl: abs(lvl.price - candle["close"]))
        self.pending_double = PendingDouble(
            target_level=nearest,
            doubles_used=closed_pos.doubles_used + 1,
            expires_at_index=idx + self.cfg.martingale_watch_candles,
        )

    def _check_pending_double(self, candle, idx, broker):
        pending = self.pending_double
        if idx > pending.expires_at_index:
            self.pending_double = None
            return
        if detect_sweep(candle, pending.target_level):
            self._open_position(
                pending.target_level,
                candle,
                idx,
                broker,
                doubles_used=pending.doubles_used,
                size_multiplier=self.cfg.martingale_multiplier ** pending.doubles_used,
            )
            self.pending_double = None
