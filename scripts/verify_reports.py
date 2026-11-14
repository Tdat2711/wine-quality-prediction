"""Verify protected bytes, report provenance, notebook errors and local links."""
import json
from pathlib import Path
import re
import sys
import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.reporting import sha256, write_json


def main():
    baseline = json.loads((ROOT / 'outputs/quality/protected_baseline.json').read_text(encoding='utf-8'))
    changed = [name for name, digest in baseline.items() if sha256(ROOT / name) != digest]
    if changed:
        raise AssertionError(f'Protected inputs changed: {changed}')
    checks = []
    for directory in ('eda', 'analysis', 'cleaning_report', 'model_report', 'feature_examples'):
        info = json.loads((ROOT / f'outputs/{directory}/summary.json').read_text(encoding='utf-8'))
        for name, digest in info['inputs'].items():
            if sha256(name) != digest:
                raise AssertionError(f'Stale report input: {directory}: {name}')
        checks.append(directory)
    notebooks = []
    for path in sorted((ROOT / 'notebooks').glob('*.ipynb')):
        notebook = nbformat.read(path, as_version=4)
        code = [c for c in notebook.cells if c.cell_type == 'code']
        if not all(c.execution_count is not None for c in code):
            raise AssertionError(f'Notebook has unexecuted cells: {path}')
        if any(o.output_type == 'error' for c in code for o in c.get('outputs', [])):
            raise AssertionError(f'Notebook has error outputs: {path}')
        notebooks.append(path.name)
    docs = [ROOT / 'README.md', ROOT / 'wine_encoding/README.md', *ROOT.glob('docs/*.md'),
            *ROOT.glob('outputs/*/*.md')]
    broken = []
    for path in docs:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                continue
            target = target.split('#')[0].strip('<>')
            if target and not (path.parent / target).exists():
                broken.append(f'{path.relative_to(ROOT)}: {target}')
    if broken:
        raise AssertionError(f'Broken local links: {broken}')
    result = {'protected_files': len(baseline), 'protected_unchanged': True,
              'report_provenance_verified': checks, 'executed_notebooks': notebooks,
              'local_markdown_links': 'pass'}
    write_json(ROOT / 'outputs/quality/verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
