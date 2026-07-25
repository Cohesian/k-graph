"""Shared k-graph.toml infrastructure resolution (used by validate + resolve)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    sys.exit("Python 3.11+ (tomllib) required")

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "k-graph.toml"

_map_cache: dict[str, dict[str, Any]] = {}


def load_config(path: Path | None = None) -> dict:
    p = path or CONFIG
    with p.open("rb") as fh:
        return tomllib.load(fh)


def node_key(rel: Path, node_id: str) -> str:
    rel_s = rel.as_posix()
    return f"{rel_s}/{node_id}" if rel_s else node_id


def tree_cfg(cfg: dict, tree: str) -> dict | None:
    """tree e.g. 'documents', 'media.scripts', 'media.videos'."""
    node = cfg.get("data", {})
    for part in tree.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node if isinstance(node, dict) else None


def tree_root(tree: str, infra: dict | None = None) -> str:
    """Content root for a tree, optionally overridden by its infrastructure."""
    configured = (infra or {}).get("root")
    if configured:
        return str(configured).strip("/")
    return "data/" + tree.replace(".", "/")


def sources(tree_spec: dict) -> list[str]:
    raw = tree_spec.get("sources") or []
    return raw if isinstance(raw, list) else []


def infra_cfg(cfg: dict, source: str) -> dict:
    """Resolve dotted source names, e.g. local.scenes -> [infrastructure.local.scenes]."""
    node = cfg.get("infrastructure", {})
    for part in source.split("."):
        if not isinstance(node, dict):
            return {}
        node = node.get(part)
    return node if isinstance(node, dict) else {}


def mapper_path(infra: dict) -> str:
    raw = infra.get("mapper", "")
    if not raw:
        raise KeyError("hash mapping requires mapper on infrastructure source")
    return raw.removeprefix("./")


def default_ext(tree: str) -> str:
    parts = tree.split(".")
    if "videos" in parts:
        return "mp4"
    if "scripts" in parts:
        return "py"
    return ""


def rel_path(root: str, key: str, ext: str) -> str:
    return f"{root}/{key}.{ext}"


def fs_path(infra: dict, root: str, key: str, ext: str) -> str:
    """Path within the selected infrastructure: ``{root}/{key}.{ext}``."""
    return rel_path(root, key, ext)


def is_local_fs(infra: dict) -> bool:
    return infra.get("mapping", "path") == "path" and not infra.get("origin", "")


def load_hash_map(path: str) -> dict[str, Any]:
    if path not in _map_cache:
        with (ROOT / path).open("rb") as fh:
            _map_cache[path] = tomllib.load(fh)
    return _map_cache[path]


def hash_for_key(infra: dict, key: str) -> str:
    path = mapper_path(infra)
    entry = load_hash_map(path).get(key)
    if entry is None:
        raise KeyError(f"no hash-map entry for {key!r} in {path}")
    value = entry.get("hash") or entry.get("ref")
    if not value:
        raise KeyError(f"hash-map entry for {key!r} has no hash/ref")
    return value


def join_origin(origin: str, pattern: str, **fields: str) -> str:
    base = origin.rstrip("/")
    segment = pattern.format(**fields)
    if segment.startswith("/"):
        return f"{base}{segment}"
    return f"{base}/{segment}"


def resolve(
    tree: str,
    key: str,
    *,
    ext: str | None = None,
    source: str | None = None,
    cfg: dict | None = None,
) -> str | Path:
    cfg = cfg or load_config()
    spec = tree_cfg(cfg, tree)
    if spec is None:
        raise KeyError(f"tree {tree!r} not in k-graph.toml")

    src = source or spec.get("serve")
    available = sources(spec)
    if src is None:
        if len(available) == 1:
            src = available[0]
        else:
            raise KeyError(f"tree {tree!r} has no serve default; pass source=")
    if src not in available:
        raise KeyError(f"source {src!r} not in {tree!r} sources {available!r}")

    infra = infra_cfg(cfg, src)
    mapping = infra.get("mapping", "path")
    root = tree_root(tree, infra)
    ext = ext or default_ext(tree) or "md"

    if mapping == "path":
        path = fs_path(infra, root, key, ext)
        origin = infra.get("origin", "")
        if not origin:
            return ROOT / path
        pattern = infra.get("pattern", "{path}")
        return join_origin(origin, pattern, path=path)

    if mapping == "hash":
        h = hash_for_key(infra, key)
        origin = infra.get("origin", "")
        if not origin:
            raise ValueError(f"source {src!r} uses hash mapping but has no origin")
        pattern = infra.get("pattern", "/{hash}")
        return join_origin(origin, pattern, hash=h)

    raise ValueError(f"unknown mapping {mapping!r} on source {src!r}")
