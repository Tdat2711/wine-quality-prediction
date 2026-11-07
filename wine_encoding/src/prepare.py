"""Run: python -m src.prepare --config config.json"""
import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.model_selection import GroupShuffleSplit

from .encoding import (SOURCE_COLUMNS, build_preprocessor, normalize,
                       select_profile_columns, with_missing_flags, read_source_csv,
                       resolve_source_path)


def main():
    parser = argparse.ArgumentParser()
    module_root = Path(__file__).resolve().parents[1]
    default_config = 'config.json' if Path('config.json').is_file() else str(module_root / 'config.json')
    parser.add_argument('--config', default=default_config)
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    cfg = json.loads(config_path.read_text(encoding='utf-8'))
    source = resolve_source_path(cfg['source'], relative_to=config_path.parent)
    output = (config_path.parent / cfg['output']).resolve()
    output.mkdir(parents=True, exist_ok=True)
    raw = read_source_csv(source)
    if set(raw.columns) != set(SOURCE_COLUMNS):
        raise ValueError(f'Unexpected source schema: {list(raw.columns)}')
    frame = normalize(raw)
    if frame.points.isna().any():
        raise ValueError('Missing targets: supply observed points for every training row')
    # A conservative title grouping; this does not prove unique physical wine identity.
    groups = (frame.title.str.normalize('NFKC').str.casefold()
              .str.replace(r'\s+', ' ', regex=True).str.strip())
    if groups.eq('').any():
        raise ValueError('Empty titles: cannot reliably group these rows')
    seed = cfg['seed']
    test_fraction = cfg['test_fraction']
    val_fraction = cfg['validation_fraction']
    if not 0 < test_fraction < 1 or not 0 < val_fraction < 1 - test_fraction:
        raise ValueError('Invalid split fractions')
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_fraction, random_state=seed)
    train_val, test = next(splitter.split(frame, groups=groups))
    splitter2 = GroupShuffleSplit(n_splits=1,
                                 test_size=val_fraction / (1 - test_fraction),
                                 random_state=seed)
    tr_local, va_local = next(splitter2.split(frame.iloc[train_val],
                                             groups=groups.iloc[train_val]))
    indices = {'train': np.sort(train_val[tr_local]),
               'validation': np.sort(train_val[va_local]), 'test': np.sort(test)}
    group_sets = {name: set(groups.iloc[idx]) for name, idx in indices.items()}
    for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]:
        if group_sets[a] & group_sets[b]:
            raise AssertionError(f'Group overlap: {a}, {b}')
    combined = np.concatenate(list(indices.values()))
    if len(np.unique(combined)) != len(frame):
        raise AssertionError('Rows lost or duplicated between splits')
    print('Split sizes:', {name: len(idx) for name, idx in indices.items()}, flush=True)
    prepared = with_missing_flags(frame.drop(columns='points'))
    preprocessor = build_preprocessor(cfg)
    train_matrix = sparse.csr_matrix(
        preprocessor.fit_transform(prepared.iloc[indices['train']]), dtype=np.float32)
    selections = select_profile_columns(preprocessor)
    names = np.asarray(preprocessor.get_feature_names_out(), dtype=str)
    joblib.dump({'preprocessor': preprocessor, 'profiles': selections,
                 'source_columns': SOURCE_COLUMNS, 'config': cfg},
                output / 'encoder.joblib', compress=3)
    manifest = pd.DataFrame({'source_row_id': np.arange(len(frame)),
                             'title_group': groups, 'split': ''})
    try:
        source_repr = str(source.relative_to(config_path.parent))
    except ValueError:
        source_repr = str(source)
    report = {'source': source_repr, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'rows': len(frame), 'target': 'points', 'seed': seed,
              'group_overlap': 0, 'fit_on': 'train only',
              'missing_by_column': {k: int(v) for k, v in raw.isna().sum().items()},
              'profiles': {p: len(cols) for p, cols in selections.items()}, 'splits': {}}
    for profile, cols in selections.items():
        dest = output / profile
        dest.mkdir(exist_ok=True)
        pd.DataFrame({'feature_index': np.arange(len(cols)), 'feature_name': names[cols]})\
            .to_csv(dest / 'features.csv', index=False, encoding='utf-8-sig')
    for split, idx in indices.items():
        matrix = train_matrix if split == 'train' else sparse.csr_matrix(
            preprocessor.transform(prepared.iloc[idx]), dtype=np.float32)
        if not np.isfinite(matrix.data).all():
            raise AssertionError(f'Non-finite encoded values in {split}')
        manifest.loc[idx, 'split'] = split
        y = frame.points.iloc[idx].to_numpy(dtype=np.float32)
        np.save(output / f'y_{split}.npy', y)
        np.save(output / f'row_ids_{split}.npy', idx)
        report['splits'][split] = {'rows': len(idx), 'title_groups': len(group_sets[split]),
                                   'points_mean': float(y.mean()),
                                   'points_min': float(y.min()), 'points_max': float(y.max())}
        for profile, cols in selections.items():
            selected = matrix[:, cols].tocsr()
            dest = output / profile
            sparse.save_npz(dest / f'X_{split}.npz', selected)
            if split == 'train':
                # Small human-readable export only; avoid a huge dense full-data CSV.
                pd.DataFrame(selected[:5].toarray(), columns=names[cols]).to_csv(
                    dest / 'sample_5_rows.csv', index=False, encoding='utf-8-sig')
        print(f'Exported {split}: {matrix.shape}', flush=True)
    manifest.to_csv(output / 'split_manifest.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame([{'column': col,
                   'encoded_feature_count': (0 if col == 'points' else
                       preprocessor.output_indices_[col].stop - preprocessor.output_indices_[col].start),
                   'role': 'target y' if col == 'points' else 'encoded X; profile-dependent'}
                  for col in raw.columns]).to_csv(output / 'column_coverage.csv', index=False)
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                       encoding='utf-8')
    print('Done. No prediction model has been trained.', flush=True)


if __name__ == '__main__':
    main()
