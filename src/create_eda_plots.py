"""Shared descriptive price plots for progress notebooks and PNG export.

Importing this module does not read data, write figures, or change the backend.
Run python src/create_eda_plots.py to refresh the existing two PNG exports.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "wine_cleaned_final.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "eda_plots"


def _number(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}".translate(str.maketrans({",": ".", ".": ","}))


def _price_sample(df_price: pd.DataFrame) -> pd.DataFrame:
    """Validate an observed-price sample without silently dropping rows."""
    missing = {"price", "points"} - set(df_price.columns)
    if missing:
        raise ValueError(f"Thiếu cột bắt buộc: {sorted(missing)}")
    if df_price.empty:
        raise ValueError("Không có bản ghi có giá để vẽ.")
    values = df_price[["price", "points"]].copy()
    for column in values.columns:
        values[column] = pd.to_numeric(values[column], errors="raise")
        if values[column].isna().any() or not np.isfinite(values[column]).all():
            raise ValueError(f"Cột {column} chứa giá trị thiếu hoặc không hữu hạn.")
    if not values["price"].gt(0).all():
        raise ValueError("Giá quan sát phải dương.")
    if not values["points"].between(80, 100).all():
        raise ValueError("Điểm review phải nằm trong khoảng 80–100.")
    return values


def plot_price_distribution(
    df_price: pd.DataFrame, *, display_max: float = 300.0
) -> Figure:
    """Plot counts and KDE on labelled axes, keeping the full input sample."""
    values = _price_sample(df_price)
    if not np.isfinite(display_max) or display_max <= 0:
        raise ValueError("Giới hạn hiển thị giá phải dương và hữu hạn.")
    prices = values["price"]
    outside = int(prices.gt(display_max).sum())

    with sns.axes_style("whitegrid"), sns.plotting_context("notebook"):
        fig, ax = plt.subplots(figsize=(11, 6.2))
        ax.hist(
            prices, bins=100, range=(0, display_max), color="#722F37",
            alpha=0.8, edgecolor="white", linewidth=0.4, label="Tần suất",
        )
        ax.axvline(
            prices.median(), color="#1E88E5", linestyle="--", linewidth=2,
            label=f"Trung vị = {_number(prices.median())} USD",
        )
        ax.axvline(
            prices.mean(), color="#EF8A17", linestyle="--", linewidth=2,
            label=f"Trung bình = {_number(prices.mean(), 1)} USD",
        )
        handles, labels = ax.get_legend_handles_labels()
        if prices.nunique() > 1:
            density_ax = ax.twinx()
            sns.kdeplot(
                x=prices, ax=density_ax, color="#A48419", linewidth=2,
                clip=(0, display_max), cut=0, label="Mật độ KDE",
            )
            density_ax.set_ylabel("Mật độ ước lượng (KDE)")
            density_ax.grid(False)
            kde_handles, kde_labels = density_ax.get_legend_handles_labels()
            handles += kde_handles
            labels += kde_labels
        ax.legend(handles, labels, loc="upper right", framealpha=0.95)
        ax.set(
            xlim=(0, display_max), xlabel="Giá (USD)",
            ylabel="Số bản ghi review",
            title="Hình 1. Phân bố giá trên mẫu có giá quan sát",
        )
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: _number(value)))
        fig.subplots_adjust(left=0.09, right=0.88, top=0.89, bottom=0.22)
        fig.text(
            0.09, 0.055,
            f"N = {_number(len(values))} bản ghi có giá; trung vị = {_number(prices.median())} USD; "
            f"trung bình = {_number(prices.mean(), 1)} USD.\n"
            f"Khung 0–{_number(display_max)} USD; {_number(outside)} bản ghi trên khung vẫn được giữ "
            f"(giá cao nhất {_number(prices.max())} USD).",
            fontsize=9, va="bottom",
        )
    return fig


def plot_price_points(
    df_price: pd.DataFrame,
    *,
    max_points: int = 15_000,
    random_state: int = 42,
    display_max: float = 300.0,
) -> Figure:
    """Draw a reproducible descriptive scatter without fitting a model."""
    values = _price_sample(df_price)
    if not isinstance(max_points, int) or max_points <= 0:
        raise ValueError("Số điểm lấy mẫu phải là số nguyên dương.")
    if not np.isfinite(display_max) or display_max <= 0:
        raise ValueError("Giới hạn hiển thị giá phải dương và hữu hạn.")
    plotted = (
        values.sample(max_points, random_state=random_state)
        if len(values) > max_points else values
    )
    visible = int(plotted["price"].le(display_max).sum())
    outside = int(values["price"].gt(display_max).sum())

    with sns.axes_style("whitegrid"), sns.plotting_context("notebook"):
        fig, ax = plt.subplots(figsize=(11, 6.2))
        scatter = ax.scatter(
            plotted["price"], plotted["points"], c=plotted["points"],
            cmap="viridis", vmin=80, vmax=100, alpha=0.35, s=14, edgecolors="none",
        )
        ax.set(
            xlim=(0, display_max), ylim=(79, 101), yticks=[80, 85, 90, 95, 100],
            xlabel="Giá (USD)", ylabel="Điểm review (points, thang 80–100)",
            title="Hình 2. Quan hệ giá và điểm review — khám phá sơ bộ",
        )
        fig.colorbar(scatter, ax=ax, pad=0.025, shrink=0.9, label="Điểm review")
        fig.subplots_adjust(left=0.09, right=0.96, top=0.89, bottom=0.22)
        fig.text(
            0.09, 0.055,
            f"Toàn mẫu: {_number(len(values))} bản ghi; lấy mẫu {_number(len(plotted))} "
            f"(seed {random_state}); {_number(visible)} điểm nằm trong khung.\n"
            f"Khung 0–{_number(display_max)} USD; toàn mẫu có {_number(outside)} bản ghi trên khung, "
            f"vẫn được giữ (tối đa {_number(values['price'].max())} USD).",
            fontsize=9, va="bottom",
        )
    return fig


def main() -> None:
    """Preserve the existing CLI and filenames; allow a chosen export folder."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DATA_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    # Only the command-line exporter selects a non-interactive backend.
    plt.switch_backend("Agg")
    df_all = pd.read_csv(args.input)
    if "price" not in df_all:
        raise ValueError("Dữ liệu thiếu cột price.")
    df_price = df_all.loc[df_all["price"].notna()].copy()
    print(
        f"Cleaned records: {len(df_all):,}; observed price: {len(df_price):,}; "
        f"missing price: {df_all['price'].isna().sum():,}"
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, plot in [
        ("fig1_price_distribution.png", plot_price_distribution),
        ("fig2_price_vs_points.png", plot_price_points),
    ]:
        fig = plot(df_price)
        destination = args.output_dir / filename
        fig.savefig(destination, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {destination}")


if __name__ == "__main__":
    main()
