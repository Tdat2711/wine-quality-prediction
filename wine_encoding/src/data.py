"""Locked split verification and artifact provenance shared by all commands."""
import hashlib
import json
from pathlib import Path


from src.split_data import create_splits, check_existing_splits
from .encoding import read_source_csv, resolve_source_path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 2
SPLITS = {'train': 'train', 'validation': 'val', 'test': 'test'}


def checksum(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load_config(path=None):
    path = Path(path or ROOT / 'config.json').resolve()
    config = json.loads(path.read_text(encoding='utf-8'))
    for key in ('source', 'split_dir', 'output'):
        config[key] = str((path.parent / config[key]).resolve())
    return config


def locked_parts(config):
    """Validate all saved splits against the canonical rule, preserving source IDs."""
    source = resolve_source_path(config['source'])
    raw = read_source_csv(source)
    parts = create_splits(raw)
    check_existing_splits(parts, directory=config['split_dir'])
    return raw, {name: parts[stored] for name, stored in SPLITS.items()}


def provenance(config):
    paths = {'source': config['source']}
    paths.update({name: str(Path(config['split_dir']) / f'{stored}.csv')
                  for name, stored in SPLITS.items()})
    return {name: {'path': str(Path(path).resolve()), 'sha256': checksum(path)}
            for name, path in paths.items()}


def validate_provenance(record):
    for name, item in record.items():
        if checksum(item['path']) != item['sha256']:
            raise ValueError(f'{name} changed; regenerate encoding/model artifacts')


def load_report(data_dir):
    report = json.loads((Path(data_dir) / 'report.json').read_text(encoding='utf-8'))
    if report.get('schema_version') != SCHEMA_VERSION:
        raise ValueError('Incompatible encoding artifact; rerun prepare')
    validate_provenance(report['provenance'])
    return report


def read_part(report, split):
    """Training calls this only for train/validation; never loads test labels."""
    return read_source_csv(report['provenance'][split]['path'])


def normalized_reviews(series):
    return series.fillna('').astype(str).str.lower().str.strip().str.replace(
        r'\s+', ' ', regex=True)


def review_matches(frame, training_reviews):
    text = normalized_reviews(frame['description'])
    return text.ne('') & text.isin(set(training_reviews) - {''})
