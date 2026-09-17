from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_distribution_installs_files_required_to_build_local_mcp() -> None:
    manifest = yaml.safe_load((ROOT / "distribution.yaml").read_text())
    owned = set(manifest["distribution_owned"])

    assert {"README.md", "pyproject.toml", "src/"}.issubset(owned)

