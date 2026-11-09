"""Verify locked splits and export train-fitted diagnostic and combined encodings."""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse

from .combined import build_encoder, feature_names
from .data import SCHEMA_VERSION, load_config, locked_parts, provenance, normalized_reviews, review_matches
from .encoding import SOURCE_COLUMNS, build_preprocessor, normalize, select_profile_columns, with_missing_flags


def prepare(config):
    if config.get('seed', 42) != 42:
        raise ValueError('Locked splits use seed 42; changing seed is not supported')
    raw, parts = locked_parts(config)
    if set(raw.columns) != set(SOURCE_COLUMNS):
        raise ValueError(f'Unexpected source schema: {list(raw.columns)}')
    # Validate every input/split before creating output artifacts.
    frames = {name: with_missing_flags(normalize(part[SOURCE_COLUMNS]))
              for name, part in parts.items()}
    record = provenance(config)
    diagnostic = build_preprocessor(config)
    diagnostic_train = sparse.csr_matrix(diagnostic.fit_transform(frames['train']), dtype=np.float32)
    profiles = select_profile_columns(diagnostic)
    combined = build_encoder(config)
    combined_train = sparse.csr_matrix(combined.fit_transform(parts['train']))
    out = Path(config['output'])
    out.mkdir(parents=True, exist_ok=True)
    report = {'schema_version': SCHEMA_VERSION, 'source': config['source'],
              'sha256': record['source']['sha256'], 'provenance': record, 'config': config,
              'rows': len(raw), 'eligible_rows': sum(map(len, parts.values())),
              'excluded_rows': len(raw) - sum(map(len, parts.values())),
              'target': 'points', 'seed': 42, 'fit_on': 'train only', 'group_overlap': 0,
              'missing_by_column': {k: int(v) for k, v in raw.isna().sum().items()},
              'profiles': {name: len(cols) for name, cols in profiles.items()}, 'splits': {}}
    report['profiles']['combined'] = combined_train.shape[1]
    joblib.dump({'schema_version': SCHEMA_VERSION, 'preprocessor': diagnostic, 'profiles': profiles,
                 'combined': combined, 'source_columns': SOURCE_COLUMNS, 'config': config,
                 'provenance': record}, out / 'encoder.joblib', compress=3)
    all_names = np.asarray(diagnostic.get_feature_names_out())
    for name, names in [(p, all_names[c]) for p, c in profiles.items()] + [('combined', feature_names(combined))]:
        dest = out / name
        dest.mkdir(exist_ok=True)
        pd.DataFrame({'feature_index': np.arange(len(names)), 'feature_name': names}).to_csv(
            dest / 'features.csv', index=False, encoding='utf-8-sig')
    manifests = []
    training_reviews = normalized_reviews(parts['train'].description)
    for name, part in parts.items():
        ids = part.index.to_numpy(dtype=np.int64)
        np.save(out / f'row_ids_{name}.npy', ids)
        np.save(out / f'y_{name}.npy', part.points.to_numpy(dtype=np.float32))
        manifests.append(pd.DataFrame({'source_row_id': ids, 'title_group': part.title_clean.to_numpy(),
                                       'split': name}))
        matrix = diagnostic_train if name == 'train' else sparse.csr_matrix(
            diagnostic.transform(frames[name]), dtype=np.float32)
        matrices = {p: matrix[:, c].tocsr() for p, c in profiles.items()}
        matrices['combined'] = combined_train if name == 'train' else sparse.csr_matrix(combined.transform(part))
        for profile, selected in matrices.items():
            if not np.isfinite(selected.data).all():
                raise ValueError(f'Non-finite encoded values: {name}/{profile}')
            sparse.save_npz(out / profile / f'X_{name}.npz', selected)
            if name == 'train':
                names = pd.read_csv(out / profile / 'features.csv').feature_name
                pd.DataFrame(selected[:5].toarray(), columns=names).to_csv(
                    out / profile / 'sample_5_rows.csv', index=False, encoding='utf-8-sig')
        report['splits'][name] = {'rows': len(part), 'title_groups': part.title_clean.nunique()}
        # Text audit only: no test target summaries or metrics.
        if name != 'train':
            report['splits'][name]['review_matches_train'] = int(review_matches(part, training_reviews).sum())
        print(f'Exported {name}: {len(part)} rows', flush=True)
    pd.concat(manifests, ignore_index=True).to_csv(out / 'split_manifest.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame([{'column': col, 'encoded_feature_count': 0 if col == 'points' else
                  diagnostic.output_indices_[col].stop - diagnostic.output_indices_[col].start,
                  'role': 'target y' if col == 'points' else 'diagnostic X; profile-dependent'}
                 for col in SOURCE_COLUMNS]).to_csv(out / 'column_coverage.csv', index=False)
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config')
    args = parser.parse_args()
    prepare(load_config(args.config))


if __name__ == '__main__':
    main()
