"""Render diagnostics from validation predictions, without refitting a model."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


def render_diagnostics(audit, alpha, mae, rmse, out):
    y = audit.points_actual.to_numpy()
    pred = audit.points_predicted.to_numpy()
    residual = y - pred
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    hb = axes[0].hexbin(y, pred, gridsize=28, mincnt=1, cmap='viridis')
    axes[0].plot([y.min(), y.max()], [y.min(), y.max()], '--', color='tomato', linewidth=1)
    axes[0].set(xlabel='Actual points', ylabel='Predicted points',
                xlim=(y.min() - 1, y.max() + 1), title='Validation: actual vs predicted')
    fig.colorbar(hb, ax=axes[0], label='Rows')
    axes[1].hexbin(pred, residual, gridsize=35, mincnt=1, cmap='viridis')
    axes[1].axhline(0, color='tomato', linestyle='--', linewidth=1)
    axes[1].set(xlabel='Predicted points', ylabel='Actual - predicted', title='Residuals on validation')
    axes[2].hist(residual, bins=45, color='#247c9c', edgecolor='white')
    axes[2].axvline(0, color='tomato', linestyle='--', linewidth=1)
    axes[2].set(xlabel='Actual - predicted', ylabel='Rows', title='Residual distribution')
    fig.suptitle(f'Ridge alpha={alpha:g} | MAE={mae:.3f} | RMSE={rmse:.3f} | n={len(y):,}')
    fig.tight_layout()
    fig.savefig(Path(out) / 'validation_diagnostics.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    out = Path(__file__).resolve().parents[1] / 'outputs/model_product'
    summary = json.loads((out / 'summary.json').read_text(encoding='utf-8'))
    render_diagnostics(pd.read_csv(out / 'validation_predictions.csv'),
                       summary['selected_alpha'], summary['validation']['MAE'],
                       summary['validation']['RMSE'], out)
