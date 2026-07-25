#!/usr/bin/env python3
"""Validate the k-graph: k-graph/ (structure) + content resolved via k-graph.toml.

Layout:
- k-graph/ yaml-only. Leaves carry `data` (abstract trees + extensions).
- k-graph.toml defines infrastructure sources (origin + mapping) and per-tree
  reachable sources, including content owned by sibling repositories. Leaf yaml
  never names a concrete host.

Checks per node:
- composite edges.g / edges.l / edges.r resolve;
- path + local filesystem source: file on disk (videos/mp4 optional — gitignored builds);
- hash source: map file contains hash/ref for the key.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("pyyaml is required: pip install pyyaml")

from kgraph_infra import (
    CONFIG,
    ROOT,
    fs_path,
    hash_for_key,
    infra_cfg,
    is_local_fs,
    load_config,
    mapper_path,
    node_key,
    sources,
    tree_cfg,
    tree_root,
)

TREE = ROOT / "k-graph"

PATH_OPTIONAL = frozenset({"data.media.videos"})

problems: list[str] = []


def err(where: Path, msg: str):
    problems.append(f"{where.relative_to(ROOT)}: {msg}")


def iter_data_entries(data: dict) -> list[tuple[str, list[str]]]:
    if not data:
        return []
    out: list[tuple[str, list[str]]] = []
    docs = data.get("documents")
    if docs is not None:
        exts = docs if isinstance(docs, list) else [docs]
        out.append(("data.documents", exts))
    media = data.get("media") or {}
    if not isinstance(media, dict):
        return out
    scripts = media.get("scripts")
    if scripts is not None:
        if isinstance(scripts, dict):
            for sub, exts in scripts.items():
                out.append((
                    f"data.media.scripts.{sub}",
                    exts if isinstance(exts, list) else [exts],
                ))
        else:
            out.append((
                "data.media.scripts",
                scripts if isinstance(scripts, list) else [scripts],
            ))
    videos = media.get("videos")
    if videos is not None:
        out.append(("data.media.videos", videos if isinstance(videos, list) else [videos]))
    return out


def sibling_ids(tree_dir: Path) -> set[str]:
    ids = {p.stem for p in tree_dir.glob("*.yaml") if p.name != "props.yaml"}
    ids |= {p.name for p in tree_dir.iterdir() if p.is_dir()}
    return ids


def check_edges(where: Path, node: dict, siblings: set[str], composite: bool):
    e = node.get("edges") or {}
    if composite:
        for child in e.get("g") or []:
            if child not in siblings:
                err(where, f"edges.g child '{child}' not found")
    l = e.get("l") or {}
    for side in ("prev", "next"):
        t = l.get(side)
        if t is not None and t not in siblings:
            err(where, f"edges.l.{side} '{t}' not found among siblings")
    for t in e.get("r") or []:
        if t not in siblings:
            err(where, f"edges.r '{t}' not found among siblings")


def check_data(leaf: Path, node: dict, rel: Path, cfg: dict):
    data = node.get("data")
    if not data:
        err(leaf, "no data block")
        return
    node_id = leaf.stem
    key = node_key(rel, node_id)
    entries = iter_data_entries(data)
    if not entries:
        err(leaf, "data block is empty")
        return

    for tree_key, exts in entries:
        tree_name = tree_key.removeprefix("data.")
        spec = tree_cfg(cfg, tree_name)
        if spec is None:
            err(leaf, f"tree '{tree_key}' not configured in k-graph.toml")
            continue

        reachable = sources(spec)
        if not reachable:
            err(leaf, f"tree '{tree_key}' has no sources")
            continue

        for src in reachable:
            infra = infra_cfg(cfg, src)
            if not infra:
                err(leaf, f"source '{src}' not in [infrastructure]")
                continue
            mapping = infra.get("mapping", "path")
            root = tree_root(tree_name, infra)

            if mapping == "path" and is_local_fs(infra):
                for ext in exts:
                    target = ROOT / fs_path(infra, root, key, ext)
                    if target.exists():
                        continue
                    if tree_key in PATH_OPTIONAL:
                        continue
                    err(leaf, f"{tree_key} [{src}] [{ext}] -> missing {target.relative_to(ROOT)}")

            elif mapping == "hash":
                try:
                    path = mapper_path(infra)
                except KeyError as exc:
                    err(leaf, f"source '{src}': {exc}")
                    continue
                map_file = ROOT / path
                if not map_file.exists():
                    err(leaf, f"hash mapper missing: {path}")
                    continue
                try:
                    hash_for_key(infra, key)
                except KeyError as exc:
                    err(leaf, str(exc))


def main():
    if not TREE.exists():
        sys.exit(f"k-graph dir not found: {TREE}")
    if not CONFIG.exists():
        sys.exit(f"config not found: {CONFIG}")
    cfg = load_config()

    n_leaves = n_composites = 0
    for dir_path in [TREE, *[p for p in TREE.rglob("*") if p.is_dir()]]:
        rel = dir_path.relative_to(TREE)
        siblings = sibling_ids(dir_path)

        props = dir_path / "props.yaml"
        if props.exists():
            n_composites += 1
            node = yaml.safe_load(props.read_text()) or {}
            if node.get("kind") not in ("T", "L"):
                err(props, f"composite kind must be T/L, got {node.get('kind')}")
            check_edges(props, node, siblings, composite=True)

        for leaf in sorted(dir_path.glob("*.yaml")):
            if leaf.name == "props.yaml":
                continue
            n_leaves += 1
            node = yaml.safe_load(leaf.read_text()) or {}
            if node.get("kind") not in ("F", "Fd"):
                err(leaf, f"leaf kind must be F/Fd, got {node.get('kind')}")
            check_edges(leaf, node, siblings, composite=False)
            check_data(leaf, node, rel, cfg)

    if problems:
        print(f"FAIL: {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print(f"OK: {n_composites} composites + {n_leaves} leaves valid; edges + content resolve.")


if __name__ == "__main__":
    main()
