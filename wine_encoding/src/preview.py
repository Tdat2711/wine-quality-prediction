"""Re-encode 100 train rows and export readable previews of saved numeric data."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from .encoding import normalize, with_missing_flags, read_source_csv


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'outputs'
    dest = output / 'preview'
    dest.mkdir(exist_ok=True)
    report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
    raw = read_source_csv(report['source'], relative_to=root)
    ids = np.load(output / 'row_ids_train.npy')[:100]
    rows = raw.iloc[ids].reset_index(drop=True)
    bundle = joblib.load(output / 'encoder.joblib')
    encoded = sparse.csr_matrix(bundle['preprocessor'].transform(
        with_missing_flags(normalize(rows.drop(columns='points')))), dtype=np.float32)
    names = np.asarray(bundle['preprocessor'].get_feature_names_out())
    for profile, columns in bundle['profiles'].items():
        x = encoded[:, columns].tocsr()
        saved = sparse.load_npz(output / profile / 'X_train.npz')[:len(ids)]
        diff = saved - x
        assert diff.nnz == 0 or np.abs(diff.data).max() < 1e-6
        frame = pd.DataFrame(x.toarray(), columns=names[columns])
        frame.insert(0, 'points_TARGET', rows.points.to_numpy())
        frame.insert(0, 'source_row_id_METADATA', ids)
        frame.to_csv(dest / f'{profile}_100_rows.csv', index=False,
                     encoding='utf-8-sig')
        print(f'{profile}: 100 rows, {x.shape[1]} numeric features, plus target and row ID')
    rows.insert(0, 'source_row_id', ids)
    rows.to_csv(dest / 'original_100_rows.csv', index=False, encoding='utf-8-sig')
    combined = sparse.csr_matrix(bundle['combined'].transform(rows))
    saved_combined = sparse.load_npz(output / 'combined/X_train.npz')[:len(ids)]
    delta = combined - saved_combined
    assert not delta.nnz or np.max(np.abs(delta.data)) < 1e-6
    combined_names = bundle['combined'].named_steps['features'].get_feature_names_out()
    pd.DataFrame(combined.toarray(), columns=combined_names).to_csv(
        dest / 'combined_100_rows.csv', index=False, encoding='utf-8-sig')
    name_index = {name: idx for idx, name in enumerate(names)}
    wanted = ['price__price', 'vintage_year__vintage_year',
              'country__country_Italy', 'country__country_Portugal',
              'country__country_US', 'variety__variety_Pinot_Gris',
              'price_missing__price_missing']
    # Actual feature names preserve spaces, unlike illustrative column labels.
    wanted[5] = 'variety__variety_Pinot Gris'
    wanted = [name for name in wanted if name in name_index]
    compact = rows[['source_row_id', 'country', 'variety', 'price',
                    'vintage_year', 'points']].head(10).copy()
    for name in wanted:
        compact[name] = encoded[:10, name_index[name]].toarray().ravel()
    compact.to_csv(dest / 'before_after_10_rows.csv', index=False, encoding='utf-8-sig')
    print('\nACTUAL BEFORE/AFTER (first 5 rows; rounded display only):')
    print(compact.head(5).round(4).to_string(index=False))
    long_rows = []
    for row_number in range(3):
        row = encoded.getrow(row_number)
        text = [(names[i], float(v)) for i, v in zip(row.indices, row.data)
                if names[i].startswith('description__')]
        for feature, value in sorted(text, key=lambda pair: -pair[1])[:8]:
            long_rows.append({'source_row_id': int(ids[row_number]),
                              'feature': feature, 'tfidf': value})
    text_frame = pd.DataFrame(long_rows)
    text_frame.to_csv(dest / 'description_tfidf_examples.csv', index=False,
                      encoding='utf-8-sig')
    print('\nTF-IDF EXAMPLES (first source row):')
    print(text_frame.head(8).round(4).to_string(index=False))
    imputer = bundle['preprocessor'].named_transformers_['price']
    print('\nPrice imputation median:', imputer.named_steps['impute'].statistics_[0])
    print('Price scaler mean:', imputer.named_steps['scale'].mean_[0])
    print('Price scaler std:', imputer.named_steps['scale'].scale_[0])
    print('\nPASS: re-encoded previews match the saved training matrices.')


if __name__ == '__main__':
    main()
