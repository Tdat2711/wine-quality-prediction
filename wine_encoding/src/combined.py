"""Serializable raw-input preparation and metadata + TF-IDF pipeline."""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

INPUT_COLUMNS = ['price', 'vintage_year', 'country', 'province', 'variety', 'description']
NUMERIC_COLUMNS = ['log_price', 'vintage_year']
CATEGORY_COLUMNS = ['country', 'province', 'variety']


class CombinedInputs(TransformerMixin, BaseEstimator):
    """Validate only model inputs; unrelated columns cannot affect predictions."""
    def fit(self, X, y=None):
        self.transform(X)
        self.n_features_in_ = len(INPUT_COLUMNS)
        return self

    def transform(self, X):
        missing = set(INPUT_COLUMNS) - set(X.columns)
        if missing:
            raise ValueError(f'Missing combined inputs: {sorted(missing)}')
        out = X[INPUT_COLUMNS].copy()
        for col in ('price', 'vintage_year'):
            original = out[col].replace(r'^\s*$', np.nan, regex=True)
            values = pd.to_numeric(original, errors='coerce').astype(float)
            if (original.notna() & values.isna()).any() or np.isinf(values).any():
                raise ValueError(f'{col}: expected finite numeric values or missing cells')
            out[col] = values
        if out.price.dropna().le(0).any():
            raise ValueError('price must be positive or missing')
        out['log_price'] = np.log1p(out.pop('price'))
        for col in CATEGORY_COLUMNS:
            values = out[col].fillna('').astype(str).str.strip()
            out[col] = values.mask(values.eq(''), '__MISSING__')
        out['description'] = out.description.fillna('').astype(str)
        return out


def build_encoder(config):
    numeric = Pipeline([
        ('impute', SimpleImputer(strategy='median', keep_empty_features=True)),
        ('scale', StandardScaler()),
    ])
    columns = ColumnTransformer([
        ('numeric', numeric, NUMERIC_COLUMNS),
        ('category', OneHotEncoder(handle_unknown='infrequent_if_exist',
             min_frequency=config['category_min_frequency'],
             max_categories=config['category_max_categories'], sparse_output=True),
             CATEGORY_COLUMNS),
        ('description', TfidfVectorizer(ngram_range=(1, 2), min_df=2,
             max_features=config['description_max_features'], sublinear_tf=True), 'description'),
    ], sparse_threshold=1.0)
    return Pipeline([('inputs', CombinedInputs()), ('features', columns)])


def build_pipeline(config, alpha):
    return Pipeline([('encode', build_encoder(config)),
                     ('ridge', Ridge(alpha=alpha, solver='lsqr', tol=1e-8, max_iter=10000))])


def feature_names(encoder):
    return encoder.named_steps['features'].get_feature_names_out()


def check_convergence(model):
    if model.n_iter_ is not None and np.max(model.n_iter_) >= model.max_iter:
        raise RuntimeError('Ridge reached iteration limit; fit is not accepted')
