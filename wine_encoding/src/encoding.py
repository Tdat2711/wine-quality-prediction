"""Shared schema and transformations; no model is trained here."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from pathlib import Path

NUMERIC = ['price', 'vintage_year', 'price_original', 'log_price']
CATEGORICAL = ['country', 'designation', 'province', 'region_1', 'region_2',
               'taster_name', 'taster_twitter_handle', 'variety', 'winery']
FLAGS = ['is_non_informative_review', 'price_was_missing', 'price_was_corrected']
TEXT = ['description', 'title']
SOURCE_COLUMNS = CATEGORICAL + NUMERIC + FLAGS + TEXT + ['points']
PRODUCT = ['price', 'vintage_year', 'country', 'designation', 'province',
           'region_1', 'region_2', 'variety', 'winery']
REVIEW = PRODUCT + ['description', 'taster_name', 'is_non_informative_review']


def resolve_source_path(path_or_str, relative_to=None) -> Path:
    """Resolve source CSV path reliably across working directories and environments."""
    p = Path(path_or_str)
    if not p.is_absolute():
        p = (Path(relative_to) if relative_to is not None else Path.cwd()) / p
    p = p.resolve()
    if not p.is_file():
        raise FileNotFoundError(f'CSV file not found: {p}')
    return p


def read_source_csv(path, relative_to=None):
    resolved_path = resolve_source_path(path, relative_to)
    frame = pd.read_csv(resolved_path)
    frame.columns = frame.columns.str.strip()
    if frame.columns.duplicated().any():
        raise ValueError('Duplicate column names after trimming header whitespace')
    return frame


def normalize(frame):
    """Deterministic conversion only: does not learn statistics from any rows."""
    required = set(SOURCE_COLUMNS) - {'points'}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f'Missing source columns: {missing}')
    out = frame.copy()
    for col in NUMERIC + (['points'] if 'points' in out else []):
        raw = out[col]
        values = pd.to_numeric(raw, errors='coerce')
        invalid = raw.notna() & raw.astype(str).str.strip().ne('') & values.isna()
        if invalid.any():
            raise ValueError(f'{col}: {int(invalid.sum())} non-numeric values')
        if np.isinf(values.dropna().to_numpy(dtype=float)).any():
            raise ValueError(f'{col}: infinite values')
        out[col] = values.astype(float)
    for col in CATEGORICAL:
        # Keep Unknown, Not applicable, and Not specified as distinct categories.
        out[col] = out[col].fillna('__MISSING__').astype(str).str.strip()
        out.loc[out[col].eq(''), col] = '__MISSING__'
    for col in TEXT:
        out[col] = out[col].fillna('').astype(str)
    mapping = {'true': 1.0, 'false': 0.0, '1': 1.0, '0': 0.0, '1.0': 1.0, '0.0': 0.0}
    for col in FLAGS:
        values = out[col].astype(str).str.strip().str.lower().map(mapping)
        if values.isna().any():
            raise ValueError(f'{col}: expected True/False or 0/1, no missing values')
        out[col] = values.astype(float)
    return out


def build_preprocessor(config):
    transformers = []
    for col in NUMERIC:
        # Add a stable missingness indicator even if train has no missing values.
        numeric = Pipeline([
            ('impute', SimpleImputer(strategy='median', keep_empty_features=True)),
            ('scale', StandardScaler()),
        ])
        transformers.append((col, numeric, [col]))
    for col in CATEGORICAL:
        transformers.append((col, OneHotEncoder(
            handle_unknown='infrequent_if_exist',
            min_frequency=config['category_min_frequency'],
            max_categories=config['category_max_categories'],
            sparse_output=True, dtype=np.float32), [col]))
    for col in FLAGS:
        transformers.append((col, 'passthrough', [col]))
    for col, limit in [('description', config['description_max_features']),
                       ('title', config['title_max_features'])]:
        transformers.append((col, TfidfVectorizer(
            max_features=limit, ngram_range=(1, 2), min_df=2,
            sublinear_tf=True, dtype=np.float32), col))
    # Input missing flags are generated before this transformer (without learning).
    for col in NUMERIC:
        transformers.append((col + '_missing', 'passthrough', [col + '_missing']))
    return ColumnTransformer(transformers, remainder='drop', sparse_threshold=1.0)


def with_missing_flags(frame):
    out = frame.copy()
    for col in NUMERIC:
        out[col + '_missing'] = out[col].isna().astype(np.float32)
    return out


def select_profile_columns(preprocessor):
    groups = {'product': PRODUCT + ['price_missing', 'vintage_year_missing'],
              'review': REVIEW + ['price_missing', 'vintage_year_missing'],
              'all_attributes_audit': list(preprocessor.output_indices_)}
    selections = {}
    for profile, columns in groups.items():
        positions = []
        for col in columns:
            if col == 'remainder':
                continue
            section = preprocessor.output_indices_[col]
            positions.extend(range(section.start, section.stop))
        selections[profile] = np.asarray(sorted(set(positions)), dtype=np.int64)
    return selections
