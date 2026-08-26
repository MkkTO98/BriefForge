#!/usr/bin/env python3
"""Register this project in an optional parent workspace registry."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
try:
    import yaml
except Exception:
    yaml = None

DEFAULT_REGISTRY = {
    'workspace': {
        'name': 'default_projectforge_workspace',
        'description': 'Shared registry for projects that may reuse compatible scaffold conventions.',
    },
    'projects': [],
    'shared_defaults': {
        'models': '../models/registry.yaml',
        'model_routing': '../models/routing.yaml',
        'skills': '../skills/',
        'instructions': '../instructions/',
        'logging_policy': '../logs/logging_policy.yaml',
        'permission_policy': '../permissions/',
    },
    'rules': [
        'Cross-project dependencies must be declared in cross_project_dependencies.yaml.',
        'Shared assets must not silently override project-local policies.',
        'Project-local decisions override workspace defaults only when recorded in artifacts/decisions/.',
        'Secrets must never be stored in the workspace registry.',
    ],
}


def require_yaml() -> None:
    if yaml is None:
        raise RuntimeError('PyYAML is required for registry writes. Run with uvx --with pyyaml or install pyyaml in a venv.')


def validate(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError('registry must be a mapping')
    if 'raw' in data:
        raise ValueError('registry contains invalid raw fallback data; repair the file before registering projects')
    data.setdefault('workspace', DEFAULT_REGISTRY['workspace'].copy())
    data.setdefault('projects', [])
    if not isinstance(data['projects'], list):
        raise ValueError('registry projects must be a list')
    for item in data['projects']:
        if not isinstance(item, dict) or 'name' not in item or 'path' not in item:
            raise ValueError('each registry project requires name and path')
    for key in ['shared_defaults', 'rules']:
        data.setdefault(key, DEFAULT_REGISTRY[key])
    return data


def load(path: Path) -> dict:
    require_yaml()
    if not path.exists():
        return DEFAULT_REGISTRY.copy()
    return validate(yaml.safe_load(path.read_text(encoding='utf-8')) or {})


def dump(path: Path, data: dict) -> None:
    require_yaml()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(validate(data), sort_keys=False), encoding='utf-8')


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--workspace', required=True); ap.add_argument('--project', required=True); ap.add_argument('--name', required=True)
    ns=ap.parse_args(); reg=Path(ns.workspace)/'projects_registry.yaml'
    try:
        data=load(reg)
        entry={'name':ns.name,'path':str(Path(ns.project).resolve()),'mode':'hybrid_inheritance'}
        data['projects']=[p for p in data['projects'] if p.get('name')!=ns.name]+[entry]
        dump(reg,data); print(reg); return 0
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
