from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
FORBIDDEN = {
    ".env",
    "auth.json",
    "state.db",
    "hermes_state.db",
    "response_store.db",
}


def load_skill(path: Path) -> dict[str, object]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    try:
        frontmatter = text.split("---\n", 2)[1]
    except IndexError as exc:
        raise ValueError(f"{path}: unterminated YAML frontmatter") from exc
    data = yaml.safe_load(frontmatter)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return data


def main() -> None:
    manifest = yaml.safe_load((ROOT / "distribution.yaml").read_text())
    if manifest.get("name") != "work-research-agent":
        raise ValueError("distribution name must be work-research-agent")
    json.loads((ROOT / "mcp.json").read_text())
    json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text())
    json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    json.loads(
        (ROOT / "plugins" / "work-research-agent" / ".codex-plugin" / "plugin.json").read_text()
    )
    json.loads((ROOT / "plugins" / "work-research-agent" / ".mcp.json").read_text())
    json.loads(
        (ROOT / "plugins" / "work-research-agent" / ".claude-plugin" / "plugin.json").read_text()
    )
    yaml.safe_load((ROOT / "config.yaml").read_text())

    skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if {path.parent.name for path in skill_paths} != {
        "work-history",
        "work-research",
        "work-status",
        "work-act",
        "dev-plan",
        "dev-implement",
    }:
        raise ValueError("the four work skills, dev-plan, and dev-implement are required")
    for path in skill_paths:
        metadata = load_skill(path)
        name = metadata.get("name")
        if name != path.parent.name or not isinstance(name, str) or not SKILL_NAME.match(name):
            raise ValueError(f"{path}: invalid skill name")
        if not metadata.get("description"):
            raise ValueError(f"{path}: description is required")
        for reference in re.findall(r"\((references/[^)]+)\)", path.read_text()):
            if not (path.parent / reference).is_file():
                raise ValueError(f"{path}: missing referenced file {reference}")

    source_root = ROOT / "skills"
    plugin_root = ROOT / "plugins" / "work-research-agent" / "skills"
    source_files = {path.relative_to(source_root) for path in source_root.rglob("*") if path.is_file()}
    plugin_files = {path.relative_to(plugin_root) for path in plugin_root.rglob("*") if path.is_file()}
    if source_files != plugin_files:
        raise ValueError("source and packaged skill files must match")
    for relative in source_files:
        if (source_root / relative).read_bytes() != (plugin_root / relative).read_bytes():
            raise ValueError(f"packaged skill differs from source: {relative}")

    tracked_names = {path.name for path in ROOT.rglob("*") if path.is_file()}
    leaked = FORBIDDEN & tracked_names
    if leaked:
        raise ValueError(f"forbidden runtime files found: {sorted(leaked)}")

    print("distribution validation passed")


if __name__ == "__main__":
    main()
