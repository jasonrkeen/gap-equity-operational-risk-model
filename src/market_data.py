"""Optional live market-price retrieval with deterministic pinned fallback."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketSnapshot:
    price: float
    status: str
    as_of: str


def get_market_snapshot(
    pinned_price: float,
    pinned_as_of: str,
    use_live: bool = False,
) -> MarketSnapshot:
    if not use_live:
        return MarketSnapshot(
            price=float(pinned_price),
            status="pinned",
            as_of=pinned_as_of,
        )

    try:
        import yfinance as yf

        history = yf.Ticker("GAP").history(period="5d", auto_adjust=False)
        if history.empty or "Close" not in history:
            raise ValueError("No usable GAP price returned")
        clean_close = history["Close"].dropna()
        if clean_close.empty:
            raise ValueError("No non-null GAP close returned")
        last_timestamp = clean_close.index[-1]
        return MarketSnapshot(
            price=float(clean_close.iloc[-1]),
            status="live",
            as_of=str(last_timestamp.date()),
        )
    except Exception:
        return MarketSnapshot(
            price=float(pinned_price),
            status="pinned_fallback",
            as_of=pinned_as_of,
        )

