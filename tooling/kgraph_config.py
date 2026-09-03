"""Load the repository-local k-graph manifest."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


def load_manifest(source_root: Path) -> dict[str, Any]:
    path = source_root / "k-graph.toml"
    try:
        with path.open("rb") as handle:
            manifest = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid k-graph.toml: {exc}") from exc
    if manifest.get("version") != 2:
        raise ValueError("k-graph.toml version must be 2")

    graph = manifest.get("graph")
    if not isinstance(graph, dict):
        raise ValueError("k-graph.toml must declare [graph]")
    if graph.get("root") != "K":
        raise ValueError("graph.root must be 'K'")
    if graph.get("authority") != "local":
        raise ValueError("graph.authority must be 'local'")
    return manifest


def storage_path(
    source_root: Path,
    manifest: dict[str, Any],
    name: str,
) -> Path:
    section = manifest.get("storage", {}).get(name, {})
    raw = section.get("path")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"storage.{name}.path must be a non-empty string")
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"storage.{name}.path must stay inside the repository")
    return source_root / path


def registered_contributors(manifest: dict[str, Any]) -> frozenset[str]:
    section = manifest.get("contributors")
    if not isinstance(section, dict):
        raise ValueError("k-graph.toml must declare [contributors]")
    values = section.get("registered")
    if not isinstance(values, list) or not values:
        raise ValueError("contributors.registered must be a non-empty string list")
    if not all(
        isinstance(value, str) and NAME_RE.fullmatch(value) is not None
        for value in values
    ):
        raise ValueError(
            "contributors.registered values must use letters, numbers, "
            "underscores, or hyphens"
        )
    if len(values) != len(set(values)):
        raise ValueError("contributors.registered contains duplicates")
    return frozenset(values)
