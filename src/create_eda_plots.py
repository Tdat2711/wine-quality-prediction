"""Reproducible train-only EDA; imports have no data or plotting side effects."""

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
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "eda"


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


def build_eda_tables(cleaned, train):
    """Describe cleaned-data audit and train features; never fit TF-IDF."""
    from sklearn.feature_extraction.text import CountVectorizer

    _price_sample(train)
    texts = train['description'].fillna('')
    lengths = texts.str.split().str.len()
    tables = {
        'audit_missing': pd.DataFrame({
            'column': cleaned.columns, 'dtype': cleaned.dtypes.astype(str).values,
            'missing': cleaned.isna().sum().values,
            'missing_pct': cleaned.isna().mean().mul(100).values}),
        'sample_counts': pd.DataFrame([
            {'sample': 'cleaned', 'rows': len(cleaned)},
            {'sample': 'observed_price', 'rows': int(cleaned['price'].notna().sum())},
            {'sample': 'missing_price', 'rows': int(cleaned['price'].isna().sum())},
            {'sample': 'train', 'rows': len(train)}]),
        'numeric_summary': train[['points', 'price', 'log_price', 'vintage_year']].describe().T,
        'points_counts': train['points'].value_counts().sort_index().rename_axis('points').reset_index(name='rows'),
        'review_summary': pd.DataFrame([{
            'rows': len(train), 'empty_reviews': int(texts.str.strip().eq('').sum()),
            'under_10_words': int(lengths.lt(10).sum()),
            'flagged_non_informative': int(train['is_non_informative_review'].sum()),
            'median_words': lengths.median(), 'min_words': lengths.min(), 'max_words': lengths.max()}]),
        'review_lengths': lengths.rename('words').to_frame(),
    }
    tiers = pd.qcut(train['price'], 4, duplicates='drop')
    tables['price_tiers'] = train.groupby(tiers, observed=True).agg(
        rows=('points', 'size'), price_median=('price', 'median'),
        points_median=('points', 'median'), points_mean=('points', 'mean'))
    tables['price_tiers'].index.name = 'price_interval_usd'
    for column in ['country', 'province', 'variety']:
        groups = train.assign(**{column: train[column].fillna('Unknown')}).groupby(column).agg(
            rows=('points', 'size'), missing_price=('price', lambda x: int(x.isna().sum())),
            price_median=('price', 'median'), points_mean=('points', 'mean'),
            points_median=('points', 'median'))
        tables[f'groups_{column}'] = groups.sort_values('rows', ascending=False)
    # Descriptive occurrence counts, including negations; no learned model weights.
    for n, label in [(1, 'unigrams'), (2, 'bigrams')]:
        vectorizer = CountVectorizer(ngram_range=(n, n), stop_words=None, min_df=1)
        try:
            matrix = vectorizer.fit_transform(texts)
        except ValueError as error:
            if 'empty vocabulary' not in str(error):
                raise
            tables[label] = pd.DataFrame(columns=['term', 'occurrences', 'documents'])
            continue
        counts = np.asarray(matrix.sum(axis=0)).ravel()
        docs = np.asarray((matrix > 0).sum(axis=0)).ravel()
        terms = pd.DataFrame({'term': vectorizer.get_feature_names_out(),
                              'occurrences': counts, 'documents': docs})
        tables[label] = terms.sort_values(['occurrences', 'term'], ascending=[False, True]).head(30).reset_index(drop=True)
    return tables


def metadata_groups(train, column, min_rows=100, top=10):
    """Select the largest groups, excluding small and placeholder groups."""
    values = train[column].fillna('Unknown')
    counts = values.value_counts()
    selected = counts[(counts >= min_rows) & ~counts.index.isin(['Unknown', 'Not applicable', 'Not specified'])]
    return list(selected.head(top).index)


def create_eda_figures(train, tables):
    """Return figures without exporting or modifying input data."""
    figures = {}
    n = len(train)
    with sns.axes_style('whitegrid'):
        fig, ax = plt.subplots(figsize=(10, 5))
        counts = tables['points_counts']
        ax.bar(counts['points'], counts['rows'], color='#722F37')
        ax.set(xlabel='Điểm review (points)', ylabel='Số bản ghi',
               title=f'Phân bố điểm review — train (n={n:,})', xticks=range(80, 101, 2))
        figures['01_points_distribution'] = fig

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        axes[0].hist(train['price'], bins=80, color='#722F37')
        axes[0].set(xlabel='Giá (USD)', ylabel='Số bản ghi', title='Giá gốc — giữ toàn bộ đuôi giá cao')
        axes[1].hist(train['log_price'], bins=60, color='#285C76')
        axes[1].set(xlabel='log1p(price)', ylabel='Số bản ghi', title='Giá sau biến đổi log1p')
        fig.suptitle(f'Phân bố giá — train (n={n:,})')
        figures['02_price_distribution'] = fig

        fig, ax = plt.subplots(figsize=(10, 5))
        sampled = train.sample(min(15000, n), random_state=42)
        ax.scatter(sampled['price'], sampled['points'], s=9, alpha=0.18, color='#285C76')
        ax.set_xscale('log')
        ax.set(xlabel='Giá (USD, trục log)', ylabel='Điểm review (points)',
               title=f'Giá và điểm — train n={n:,}; hiển thị {len(sampled):,}, seed 42')
        figures['03_price_points'] = fig

        for column, label in [('country', 'quốc gia'), ('province', 'vùng'), ('variety', 'giống nho')]:
            order = metadata_groups(train, column)
            fig, ax = plt.subplots(figsize=(12, 6))
            selected = train.loc[train[column].isin(order)]
            if order:
                sns.boxplot(data=selected, x='points', y=column, order=order, ax=ax, color='#A8C7D4', fliersize=1)
                counts = train[column].value_counts()
                ax.set_yticks(range(len(order)), [f'{value} (n={counts[value]:,})' for value in order])
            else:
                ax.text(0.5, 0.5, 'Không có nhóm đạt ngưỡng 100 bản ghi', ha='center', transform=ax.transAxes)
            ax.set(xlabel='Điểm review (points)', ylabel='',
                   title=f'Điểm theo {label} — tối đa 10 nhóm đông nhất, n nhóm ≥ 100 (train)')
            figures[f'04_{column}_points'] = fig

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(tables['review_lengths']['words'], bins=60, color='#285C76')
        ax.set(xlabel='Số từ (tách theo khoảng trắng)', ylabel='Số review',
               title=f'Độ dài review — train (n={n:,}); không tự loại review ngắn')
        figures['05_review_length'] = fig

        for label in ['unigrams', 'bigrams']:
            fig, ax = plt.subplots(figsize=(10, 6))
            top = tables[label].head(15).iloc[::-1]
            ax.barh(top['term'], top['occurrences'], color='#285C76')
            ax.set(xlabel='Tổng số lần xuất hiện trên train', ylabel='',
                   title=f'{label.capitalize()} phổ biến — giữ stopword và từ phủ định')
            figures[f'06_{label}'] = fig
    for fig in figures.values():
        fig.tight_layout()
    return figures


def run_eda(output_dir=OUTPUT_DIR):
    """Read audit data plus train; read only text/title from held-out splits."""
    from src.split_data import review_overlap

    cleaned = pd.read_csv(DATA_PATH)
    split_dir = DATA_PATH.parent / 'splits'
    train = pd.read_csv(split_dir / 'train.csv')
    tables = build_eda_tables(cleaned, train)
    text_parts = {'train': train[['description']]}
    for name in ['val', 'test']:
        text_parts[name] = pd.read_csv(split_dir / f'{name}.csv', usecols=['description'])
    tables['review_overlap'] = review_overlap(text_parts)
    out = Path(output_dir)
    (out / 'tables').mkdir(parents=True, exist_ok=True)
    (out / 'figures').mkdir(parents=True, exist_ok=True)
    indexed = {'numeric_summary', 'price_tiers', 'review_lengths',
               'groups_country', 'groups_province', 'groups_variety'}
    for name, table in tables.items():
        table.to_csv(out / 'tables' / f'{name}.csv', index=name in indexed)
    figures = create_eda_figures(train, tables)
    for name, fig in figures.items():
        fig.savefig(out / 'figures' / f'{name}.png', dpi=160, bbox_inches='tight')
        plt.close(fig)
    return tables


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    plt.switch_backend('Agg')
    # Support both direct invocation and module imports from notebooks.
    import sys
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    tables = run_eda(args.output_dir)
    print(tables['sample_counts'].to_string(index=False))
    print(tables['review_overlap'].to_string(index=False))
    print(f'EDA saved to: {args.output_dir}')


if __name__ == '__main__':
    main()
