"""Execute all four notebooks in fresh kernels using this Python environment.

Only notebook outputs/reports are written. Checksums protect data and fitted
artifacts even if a notebook accidentally attempts to change them.
"""
import hashlib
import argparse
import json
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]


def protected_hashes():
    paths = [*ROOT.glob('data/**/*.csv'), *ROOT.glob('wine_encoding/outputs/**/*')]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def main():
    available = sorted((ROOT / 'notebooks').glob('*.ipynb'))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook', choices=[p.name for p in available], help='Only execute this notebook')
    args = parser.parse_args()
    before = protected_hashes()
    results = []
    runtime = ROOT / 'outputs/quality/kernel-runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    try:
        for path in available:
            if args.notebook and path.name != args.notebook:
                continue
            print(f'Executing {path.name}', flush=True)
            notebook = nbformat.read(path, as_version=4)
            manager = KernelManager(kernel_name='python3', connection_file=str(runtime / f'{path.stem}.json'))
            manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
            client = NotebookClient(notebook, km=manager, timeout=600, startup_timeout=60,
                                    resources={'metadata': {'path': str(ROOT)}},
                                    on_cell_start=lambda cell, cell_index: print(f'  cell {cell_index}', flush=True))
            try:
                client.execute()
            finally:
                if manager.has_kernel:
                    manager.shutdown_kernel(now=True)
                manager.cleanup_resources()
            errors = [o for c in notebook.cells if c.cell_type == 'code'
                      for o in c.get('outputs', []) if o.output_type == 'error']
            if errors:
                raise AssertionError(f'Notebook errors: {path}')
            nbformat.write(notebook, path)
            results.append({'notebook': path.name, 'code_cells': sum(c.cell_type == 'code' for c in notebook.cells),
                            'errors': len(errors)})
            print(f'PASS {path.name}', flush=True)
    finally:
        after = protected_hashes()
        if before != after:
            raise AssertionError('Protected data or model artifacts changed during notebook execution')
    out = ROOT / 'outputs/quality'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'notebooks.json').write_text(json.dumps({'python': sys.version, 'notebooks': results,
                                                  'protected_files': len(before), 'unchanged': True},
                                                 indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
