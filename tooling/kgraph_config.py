"""Load the repository-local k-graph manifest."""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def load_manifest(source_root: Path) -> dict[str, Any]:
    path = source_root / "k-graph.toml"
    try:
        with path.open("rb") as handle:
            manifest = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid k-graph.toml: {exc}") from exc
    if manifest.get("version") != 1:
        raise ValueError("k-graph.toml version must be 1")

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


def contributor_formats(manifest: dict[str, Any]) -> dict[str, frozenset[str]]:
    raw_contributors = manifest.get("contributors")
    if not isinstance(raw_contributors, dict) or not raw_contributors:
        raise ValueError("k-graph.toml must declare contributors")

    out: dict[str, frozenset[str]] = {}
    for contributor, config in raw_contributors.items():
        if not isinstance(contributor, str) or not contributor:
            raise ValueError("contributor ids must be non-empty strings")
        if not isinstance(config, dict):
            raise ValueError(f"contributors.{contributor} must be a table")
        formats = config.get("formats")
        if not isinstance(formats, list) or not all(
            isinstance(value, str) and value for value in formats
        ):
            raise ValueError(
                f"contributors.{contributor}.formats must be a string list"
            )
        if len(formats) != len(set(formats)):
            raise ValueError(f"contributors.{contributor}.formats contains duplicates")
        out[contributor] = frozenset(formats)
    return out
