"""Chart generation for the executive brief and analyst outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


NAVY = "#132238"
BLUE = "#2F6BFF"
TEAL = "#11A7A0"
GOLD = "#F2B134"
RED = "#D9534F"
GRAY = "#687385"
LIGHT = "#EEF2F7"


def _finish(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def scenario_valuation_chart(valuations: pd.DataFrame, path: Path) -> Path:
    ordered = valuations.copy()
    x = np.arange(len(ordered))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    ax.bar(
        x - width,
        ordered["earnings_value"],
        width,
        label="Earnings value",
        color=BLUE,
    )
    ax.bar(x, ordered["dcf_value"], width, label="DCF value", color=TEAL)
    ax.bar(
        x + width,
        ordered["blended_value"],
        width,
        label="Blended value",
        color=GOLD,
    )
    ax.set_xticks(x, ordered["scenario"])
    ax.set_ylabel("Implied value per share ($)")
    ax.set_title("Scenario Valuation Range")
    ax.grid(axis="y", color=LIGHT, linewidth=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    for index, value in enumerate(ordered["blended_value"]):
        ax.text(index + width, value + 0.45, f"${value:.1f}", ha="center", fontsize=8)
    return _finish(fig, path)


def monte_carlo_chart(
    simulations: pd.DataFrame,
    current_price: float,
    summary: dict[str, float],
    path: Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    prices = simulations["simulated_price"]
    ax.hist(prices, bins=70, color=BLUE, alpha=0.82, edgecolor="white", linewidth=0.2)
    ax.axvline(current_price, color=RED, linewidth=2, label=f"Reference ${current_price:.2f}")
    ax.axvline(
        summary["median"],
        color=GOLD,
        linewidth=2,
        label=f"Median ${summary['median']:.2f}",
    )
    ax.axvspan(summary["p05"], summary["p95"], color=TEAL, alpha=0.10, label="5th-95th percentile")
    ax.set_xlabel("One-year simulated value per share ($)")
    ax.set_ylabel("Simulation count")
    ax.set_title("Monte Carlo Equity-Value Distribution")
    ax.grid(axis="y", color=LIGHT, linewidth=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    return _finish(fig, path)


def risk_matrix_chart(scored_risks: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    sizes = 90 + scored_risks["weight"] * 650
    colors = scored_risks["adjusted_score"]
    scatter = ax.scatter(
        scored_risks["likelihood"],
        scored_risks["impact"],
        s=sizes,
        c=colors,
        cmap="YlOrRd",
        vmin=20,
        vmax=100,
        alpha=0.85,
        edgecolor=NAVY,
        linewidth=0.7,
    )
    label_offsets = {
        "Tariffs": (5, 6),
        "Consumer": (-48, 7),
        "Old Navy": (5, -12),
        "Sourcing": (5, 6),
        "Cyber": (-20, 7),
        "Athleta": (5, 6),
        "Promotions": (5, 6),
        "Buybacks": (5, 6),
    }
    for _, row in scored_risks.iterrows():
        label = str(row["short_label"])
        offset = label_offsets.get(label, (5, 5))
        ax.annotate(
            label,
            (row["likelihood"], row["impact"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=7.5,
        )
    ax.set_xlim(0.7, 5.3)
    ax.set_ylim(0.7, 5.3)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Likelihood")
    ax.set_ylabel("Financial impact")
    ax.set_title("Operational Risk Matrix")
    ax.grid(color=LIGHT, linewidth=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("Adjusted risk score")
    return _finish(fig, path)


def brand_performance_chart(brands: pd.DataFrame, path: Path) -> Path:
    ordered = brands.sort_values("q1_2026_comp_sales_pct")
    colors = [RED if value < 0 else TEAL for value in ordered["q1_2026_comp_sales_pct"]]
    fig, ax = plt.subplots(figsize=(9.0, 4.7))
    bars = ax.barh(
        ordered["brand"],
        ordered["q1_2026_comp_sales_pct"],
        color=colors,
        alpha=0.9,
    )
    ax.axvline(0, color=NAVY, linewidth=0.8)
    ax.set_xlabel("Q1 FY2026 comparable-sales growth (%)")
    ax.set_title("Brand Performance Is Highly Uneven")
    ax.grid(axis="x", color=LIGHT, linewidth=0.9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for bar, value in zip(bars, ordered["q1_2026_comp_sales_pct"]):
        x_position = value + 0.35
        ax.text(
            x_position,
            bar.get_y() + bar.get_height() / 2,
            f"{value:+.0f}%",
            va="center",
            ha="left",
            fontsize=9,
            color="white" if value < 0 else "black",
            fontweight="bold" if value < 0 else "normal",
        )
    return _finish(fig, path)


def sensitivity_chart(sensitivity: pd.DataFrame, path: Path) -> Path:
    pivot = sensitivity.pivot(
        index="operating_margin",
        columns="pe_multiple",
        values="implied_price",
    )
    fig, ax = plt.subplots(figsize=(8.7, 5.2))
    image = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), [f"{value:.1f}x" for value in pivot.columns])
    ax.set_yticks(
        range(len(pivot.index)),
        [f"{value:.1%}" for value in pivot.index],
    )
    ax.set_xlabel("Forward P/E multiple")
    ax.set_ylabel("Operating margin")
    ax.set_title("Equity Value Sensitivity")
    for row in range(pivot.shape[0]):
        for column in range(pivot.shape[1]):
            value = pivot.iloc[row, column]
            ax.text(column, row, f"${value:.1f}", ha="center", va="center", fontsize=8)
    cbar = fig.colorbar(image, ax=ax, pad=0.02)
    cbar.set_label("Implied price ($)")
    return _finish(fig, path)


def sourcing_chart(sourcing: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    colors = [BLUE, TEAL, GRAY]
    bars = ax.bar(
        sourcing["country"],
        sourcing["purchase_share_pct"],
        color=colors[: len(sourcing)],
    )
    ax.set_ylabel("Share of FY2025 merchandise purchases (%)")
    ax.set_title("Merchandise Sourcing Concentration")
    ax.set_ylim(0, max(sourcing["purchase_share_pct"]) * 1.25)
    ax.grid(axis="y", color=LIGHT, linewidth=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, sourcing["purchase_share_pct"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1,
            f"{value:.0f}%",
            ha="center",
        )
    return _finish(fig, path)
