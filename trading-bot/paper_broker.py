from dataclasses import dataclass


@dataclass
class Trade:
    direction: str
    entry_price: float
    exit_price: float
    size_usd: float
    pnl_usd: float
    reason: str


class PaperBroker:
    """Simulated broker - tracks a virtual balance and never sends real orders."""

    def __init__(self, starting_balance_usd: float):
        self.balance = starting_balance_usd
        self.starting_balance = starting_balance_usd
        self._open = None  # (direction, entry_price, size_usd)
        self.trades: list[Trade] = []

    def open(self, direction: str, price: float, size_usd: float) -> None:
        self._open = (direction, price, size_usd)
        print(f"[OPEN]  {direction.upper():5} @ {price:.4f}  size=${size_usd:.2f}")

    def close(self, direction: str, price: float, size_usd: float, reason: str) -> None:
        entry_direction, entry_price, _ = self._open
        pct_move = (price - entry_price) / entry_price
        if entry_direction == "short":
            pct_move = -pct_move
        pnl = size_usd * pct_move
        self.balance += pnl
        self.trades.append(Trade(entry_direction, entry_price, price, size_usd, pnl, reason))
        self._open = None
        print(
            f"[CLOSE] {entry_direction.upper():5} @ {price:.4f}  "
            f"pnl=${pnl:+.2f}  reason={reason}  balance=${self.balance:.2f}"
        )

    def summary(self) -> dict:
        wins = [t for t in self.trades if t.pnl_usd > 0]
        return {
            "trades": len(self.trades),
            "wins": len(wins),
            "win_rate_pct": round(len(wins) / len(self.trades) * 100, 1) if self.trades else 0.0,
            "net_pnl_usd": round(self.balance - self.starting_balance, 2),
            "ending_balance_usd": round(self.balance, 2),
        }
