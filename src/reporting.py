"""Small shared helpers for read-only analysis and reproducible reports."""
import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0'


def sha256(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'Missing input: {path.resolve()}')
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def metadata(paths, scope, seed=None):
    return {'tool_version': VERSION, 'generated_at': datetime.now(timezone.utc).isoformat(),
            'scope': scope, 'seed': seed, 'python': platform.python_version(),
            'packages': {p: importlib.metadata.version(p) for p in
                         ('numpy', 'pandas', 'scipy', 'scikit-learn', 'matplotlib', 'joblib')},
            'inputs': {str(Path(p).resolve()): sha256(p) for p in paths}}


def output_directory(path, inputs=()):
    """Never let an additive report overwrite data or existing model artifacts."""
    out = Path(path).resolve()
    forbidden = [ROOT / 'data', ROOT / 'wine_encoding/outputs']
    for protected in forbidden:
        if out == protected or out.is_relative_to(protected) or protected.is_relative_to(out):
            raise ValueError(f'Report output overlaps protected directory: {out}')
    for source in inputs:
        source = Path(source).resolve()
        if out == source or source.is_relative_to(out):
            raise ValueError(f'Report output overlaps input: {source}')
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def markdown_table(frame):
    """No optional tabulate dependency; escape multiline text and pipes."""
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', '<br>').replace('\r', '')
    rows = ['| ' + ' | '.join(map(cell, frame.columns)) + ' |',
            '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |']
    rows.extend('| ' + ' | '.join(map(cell, row)) + ' |' for row in frame.itertuples(index=False, name=None))
    return '\n'.join(rows)
