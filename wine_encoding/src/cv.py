"""Title/review connected groups and preprocessing fitted independently per fold."""
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

from src.split_data import normalize_title
from .combined import build_encoder, check_convergence
from .data import normalized_reviews


def metrics(y, pred):
    if not np.isfinite(pred).all():
        raise ValueError('Non-finite predictions')
    if not len(y):
        return {'n': 0, 'MAE': None, 'RMSE': None, 'R2': None}
    return {'n': len(y), 'MAE': float(mean_absolute_error(y, pred)),
            'RMSE': float(np.sqrt(mean_squared_error(y, pred))),
            'R2': float(r2_score(y, pred)) if len(y) >= 2 else None}


def connected_groups(frame):
    """Transitive union of same canonical title OR same nonempty review."""
    parent = np.arange(len(frame))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for values in (frame.title.map(normalize_title), normalized_reviews(frame.description)):
        seen = {}
        for i, value in enumerate(values):
            if not value:
                continue
            if value in seen:
                parent[find(i)] = find(seen[value])
            else:
                seen[value] = i
    return np.array([find(i) for i in range(len(frame))])


def cross_validate(frame, config, alphas, folds=5):
    groups = connected_groups(frame)
    if len(np.unique(groups)) < folds:
        raise ValueError(f'Need at least {folds} independent title/review groups')
    y = frame.points.to_numpy(dtype=float)
    rows, assignments = [], np.full(len(frame), -1, dtype=int)
    for fold, (train_ids, val_ids) in enumerate(GroupKFold(n_splits=folds).split(frame, y, groups)):
        # One encoder per fold, reused across alphas only within that fold.
        encoder = build_encoder(config)
        x_train = encoder.fit_transform(frame.iloc[train_ids])
        x_val = encoder.transform(frame.iloc[val_ids])
        assignments[val_ids] = fold
        baseline = DummyRegressor(strategy='mean').fit(x_train, y[train_ids])
        rows.append({'fold': fold, 'model': 'Baseline_mean', 'alpha': np.nan,
                     **metrics(y[val_ids], baseline.predict(x_val))})
        for alpha in sorted(set(alphas)):
            model = Ridge(alpha=alpha, solver='lsqr', tol=1e-8, max_iter=10000)
            model.fit(x_train, y[train_ids])
            check_convergence(model)
            rows.append({'fold': fold, 'model': 'Ridge', 'alpha': alpha,
                         **metrics(y[val_ids], model.predict(x_val))})
        print(f'CV fold {fold + 1}/{folds} done', flush=True)
    scores = pd.DataFrame(rows)
    means = scores[scores.model.eq('Ridge')].groupby('alpha', as_index=False)[['MAE', 'RMSE', 'R2']].mean()
    winner = means.sort_values(['MAE', 'RMSE', 'alpha']).iloc[0]
    return float(winner.alpha), scores, means, pd.DataFrame({'cv_group': groups, 'fold': assignments})
