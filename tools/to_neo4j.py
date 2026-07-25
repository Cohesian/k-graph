#!/usr/bin/env python3
"""Express the local Directory Projection as Neo4j-readable Cypher.

The tool reads the complete directory/YAML k-graph, validates it, and emits a
reviewable property-graph expression. It never connects to Neo4j and never
modifies the Directory Projection.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("pyyaml is required: python -m pip install pyyaml")


KINDS = frozenset({"T", "L", "F", "Fd"})
COMPOSITES = frozenset({"T", "L"})
LEAVES = frozenset({"F", "Fd"})


@dataclass
class Node:
    key: str
    local_id: str
    kind: str
    title: str
    description: str
    source_path: Path
    parent_dir: Path
    research: list[str] = field(default_factory=list)
    media_scenes: list[str] = field(default_factory=list)
    media_videos: list[str] = field(default_factory=list)
    legacy_edges: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GroupEdge:
    origin: str
    target: str
    position: int


@dataclass(frozen=True)
class RelatedEdge:
    origin: str
    target: str
    weight: float | None = None


@dataclass
class Migration:
    source_root: Path
    tree_root: Path
    nodes: dict[str, Node] = field(default_factory=dict)
    groups: list[GroupEdge] = field(default_factory=list)
    linear: set[tuple[str, str]] = field(default_factory=set)
    related: list[RelatedEdge] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def warn(self, path: Path, message: str) -> None:
        self.warnings.append(f"{display_path(path, self.source_root)}: {message}")

    def error(self, path: Path, message: str) -> None:
        self.errors.append(f"{display_path(path, self.source_root)}: {message}")


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def unique_strings(values: list[Any]) -> list[str]:
    out: list[str] = []
    for value in values:
        if isinstance(value, str) and value not in out:
            out.append(value)
    return out


def load_yaml(path: Path, migration: Migration) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        migration.error(path, f"cannot read YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        migration.error(path, "node YAML must be a mapping")
        return {}
    return value


def key_for_directory(tree_root: Path, directory: Path) -> str:
    relative = directory.relative_to(tree_root)
    return "K" if relative == Path(".") else relative.as_posix()


def key_for_leaf(tree_root: Path, leaf: Path) -> str:
    relative_parent = leaf.parent.relative_to(tree_root)
    return (
        leaf.stem
        if relative_parent == Path(".")
        else (relative_parent / leaf.stem).as_posix()
    )


def normalize_data(
    raw: dict[str, Any],
    *,
    key: str,
    path: Path,
    youtube_keys: set[str],
    migration: Migration,
) -> tuple[list[str], list[str], list[str]]:
    data = raw.get("data") or {}
    if not isinstance(data, dict):
        migration.error(path, "data must be a mapping")
        data = {}

    research: list[str] = []
    scenes: list[str] = []
    videos: list[str] = []

    documents = unique_strings(as_list(data.get("documents")))
    research.extend(documents)

    legacy_research = unique_strings(as_list(data.get("research")))
    for value in legacy_research:
        if value not in research:
            research.append(value)

    media = data.get("media") or {}
    if not isinstance(media, dict):
        migration.error(path, "data.media must be a mapping")
        media = {}

    scripts = media.get("scripts") or {}
    if scripts and not isinstance(scripts, dict):
        migration.error(path, "data.media.scripts must be a mapping")
        scripts = {}

    legacy_scenes = unique_strings(as_list(scripts.get("scenes")))
    target_scenes = unique_strings(as_list(media.get("scenes")))
    for value in [*legacy_scenes, *target_scenes]:
        if value not in scenes:
            scenes.append(value)

    for value in unique_strings(as_list(media.get("videos"))):
        if value not in videos:
            videos.append(value)

    if key in youtube_keys and "youtube" not in videos:
        videos.append("youtube")

    return research, scenes, videos


def load_youtube_keys(source_root: Path, migration: Migration) -> set[str]:
    mapper = source_root / "maps" / "youtube.toml"
    if not mapper.exists():
        return set()
    try:
        with mapper.open("rb") as handle:
            value = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        migration.error(mapper, f"cannot read YouTube mapper: {exc}")
        return set()
    return set(value)


def add_node(
    migration: Migration,
    *,
    key: str,
    local_id: str,
    path: Path,
    parent_dir: Path,
    raw: dict[str, Any],
    allowed_kinds: frozenset[str],
    youtube_keys: set[str],
) -> None:
    kind = raw.get("kind")
    if kind not in allowed_kinds:
        migration.error(
            path,
            f"kind must be one of {sorted(allowed_kinds)}, got {kind!r}",
        )
        return

    title = raw.get("title")
    description = raw.get("description")
    if not isinstance(title, str) or not title.strip():
        migration.error(path, "title must be a non-empty string")
        title = ""
    if not isinstance(description, str) or not description.strip():
        migration.error(path, "description must be a non-empty string")
        description = ""

    if key in migration.nodes:
        migration.error(path, f"duplicate graph key {key!r}")
        return

    research, scenes, videos = normalize_data(
        raw,
        key=key,
        path=path,
        youtube_keys=youtube_keys,
        migration=migration,
    )
    edges = raw.get("edges") or {}
    if not isinstance(edges, dict):
        migration.error(path, "edges must be a mapping")
        edges = {}

    migration.nodes[key] = Node(
        key=key,
        local_id=local_id,
        kind=kind,
        title=title.strip(),
        description=description.strip(),
        source_path=path,
        parent_dir=parent_dir,
        research=research,
        media_scenes=scenes,
        media_videos=videos,
        legacy_edges=edges,
    )


def discover_nodes(migration: Migration, youtube_keys: set[str]) -> None:
    tree_root = migration.tree_root
    if not tree_root.is_dir():
        migration.errors.append(f"k-graph directory not found: {tree_root}")
        return

    directories = [tree_root, *sorted(path for path in tree_root.rglob("*") if path.is_dir())]
    for directory in directories:
        props = directory / "props.yaml"
        if not props.exists():
            migration.error(directory, "composite directory has no props.yaml")
            continue
        raw = load_yaml(props, migration)
        add_node(
            migration,
            key=key_for_directory(tree_root, directory),
            local_id="K" if directory == tree_root else directory.name,
            path=props,
            parent_dir=directory.parent,
            raw=raw,
            allowed_kinds=COMPOSITES,
            youtube_keys=youtube_keys,
        )

        for leaf in sorted(directory.glob("*.yaml")):
            if leaf.name == "props.yaml":
                continue
            raw_leaf = load_yaml(leaf, migration)
            add_node(
                migration,
                key=key_for_leaf(tree_root, leaf),
                local_id=leaf.stem,
                path=leaf,
                parent_dir=directory,
                raw=raw_leaf,
                allowed_kinds=LEAVES,
                youtube_keys=youtube_keys,
            )


def child_nodes(migration: Migration, parent_key: str) -> dict[str, str]:
    parent = migration.nodes[parent_key]
    directory = parent.source_path.parent
    children: dict[str, str] = {}
    for node in migration.nodes.values():
        if node.key == parent_key:
            continue
        if node.kind in COMPOSITES and node.source_path.parent.parent == directory:
            children[node.local_id] = node.key
        elif node.kind in LEAVES and node.source_path.parent == directory:
            children[node.local_id] = node.key
    return children


def siblings(migration: Migration, node: Node) -> dict[str, str]:
    directory = node.source_path.parent if node.kind in LEAVES else node.source_path.parent.parent
    out: dict[str, str] = {}
    for candidate in migration.nodes.values():
        candidate_directory = (
            candidate.source_path.parent
            if candidate.kind in LEAVES
            else candidate.source_path.parent.parent
        )
        if candidate_directory == directory:
            out[candidate.local_id] = candidate.key
    return out


def resolve_local_target(
    migration: Migration,
    node: Node,
    target: Any,
    *,
    edge_name: str,
) -> str | None:
    if target is None:
        return None
    if not isinstance(target, str) or not target:
        migration.error(node.source_path, f"{edge_name} target must be a non-empty string")
        return None
    candidates = siblings(migration, node)
    key = candidates.get(target)
    if key is None:
        migration.error(
            node.source_path,
            f"{edge_name} target {target!r} is not a sibling node",
        )
    return key


def build_group_edges(migration: Migration) -> None:
    for node in migration.nodes.values():
        if node.kind not in COMPOSITES:
            continue
        available = child_nodes(migration, node.key)
        raw_group = as_list(node.legacy_edges.get("g"))
        seen: set[str] = set()
        for position, child_id in enumerate(raw_group):
            if not isinstance(child_id, str) or not child_id:
                migration.error(node.source_path, "edges.g entries must be non-empty strings")
                continue
            target = available.get(child_id)
            if target is None:
                migration.error(
                    node.source_path,
                    f"edges.g child {child_id!r} is not an immediate directory child",
                )
                continue
            if child_id in seen:
                migration.error(node.source_path, f"edges.g repeats child {child_id!r}")
                continue
            seen.add(child_id)
            migration.groups.append(GroupEdge(node.key, target, position))

        unlisted = sorted(set(available) - seen)
        for child_id in unlisted:
            migration.error(
                node.source_path,
                f"immediate child {child_id!r} is absent from edges.g",
            )


def build_linear_edges(migration: Migration) -> None:
    declared_prev: dict[str, str | None] = {}
    declared_next: dict[str, str | None] = {}

    for node in migration.nodes.values():
        linear = node.legacy_edges.get("l") or {}
        if not isinstance(linear, dict):
            migration.error(node.source_path, "edges.l must be a mapping")
            continue
        declared_prev[node.key] = resolve_local_target(
            migration,
            node,
            linear.get("prev"),
            edge_name="edges.l.prev",
        )
        declared_next[node.key] = resolve_local_target(
            migration,
            node,
            linear.get("next"),
            edge_name="edges.l.next",
        )

    claims: set[tuple[str, str]] = set()
    for key, target in declared_next.items():
        if target is not None:
            claims.add((key, target))
    for key, source in declared_prev.items():
        if source is not None:
            claims.add((source, key))

    for origin, target in sorted(claims):
        if declared_next.get(origin) != target:
            migration.error(
                migration.nodes[target].source_path,
                f"prev points to {migration.nodes[origin].local_id!r}, but its next is not reciprocal",
            )
        if declared_prev.get(target) != origin:
            migration.error(
                migration.nodes[origin].source_path,
                f"next points to {migration.nodes[target].local_id!r}, but its prev is not reciprocal",
            )

    outgoing = Counter(origin for origin, _ in claims)
    incoming = Counter(target for _, target in claims)
    for key, count in outgoing.items():
        if count > 1:
            migration.error(migration.nodes[key].source_path, "more than one outgoing NEXT")
    for key, count in incoming.items():
        if count > 1:
            migration.error(migration.nodes[key].source_path, "more than one incoming NEXT")

    migration.linear = claims


def build_related_edges(migration: Migration) -> None:
    for node in migration.nodes.values():
        for entry in as_list(node.legacy_edges.get("r")):
            weight: float | None = None
            target_value = entry
            if isinstance(entry, dict):
                target_value = entry.get("target")
                raw_weight = entry.get("weight")
                if raw_weight is not None:
                    if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
                        migration.error(node.source_path, "edges.r weight must be numeric")
                        continue
                    weight = float(raw_weight)
            target = resolve_local_target(
                migration,
                node,
                target_value,
                edge_name="edges.r",
            )
            if target is not None:
                migration.related.append(RelatedEdge(node.key, target, weight))


def validate_graph(migration: Migration) -> None:
    if "K" not in migration.nodes:
        migration.errors.append("distinguished root K was not discovered")
        return

    incoming = Counter(edge.target for edge in migration.groups)
    if incoming["K"]:
        migration.error(migration.nodes["K"].source_path, "K must not have a grouping parent")
    for key, node in migration.nodes.items():
        expected = 0 if key == "K" else 1
        if incoming[key] != expected:
            migration.error(
                node.source_path,
                f"expected {expected} grouping parent(s), found {incoming[key]}",
            )

    adjacency: dict[str, list[str]] = {key: [] for key in migration.nodes}
    for edge in migration.groups:
        adjacency[edge.origin].append(edge.target)

    state: dict[str, int] = {}

    def visit(key: str) -> None:
        marker = state.get(key, 0)
        if marker == 1:
            migration.error(migration.nodes[key].source_path, "grouping cycle detected")
            return
        if marker == 2:
            return
        state[key] = 1
        for child in adjacency[key]:
            visit(child)
        state[key] = 2

    visit("K")
    unreachable = sorted(set(migration.nodes) - set(state))
    for key in unreachable:
        migration.error(migration.nodes[key].source_path, "node is not reachable from K")


def load_directory_graph(source_root: Path) -> Migration:
    source_root = source_root.resolve()
    migration = Migration(source_root=source_root, tree_root=source_root / "k-graph")
    youtube_keys = load_youtube_keys(source_root, migration)
    discover_nodes(migration, youtube_keys)
    if migration.nodes:
        build_group_edges(migration)
        build_linear_edges(migration)
        build_related_edges(migration)
        validate_graph(migration)
    return migration


def cypher_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def emit_cypher(migration: Migration) -> str:
    lines = [
        "// Generated by tools/to_neo4j.py.",
        "// Neo4j expression of the local Directory Projection.",
        "",
        "CREATE CONSTRAINT k_node_key IF NOT EXISTS",
        "FOR (n:KNode)",
        "REQUIRE n.key IS UNIQUE;",
        "",
        "CREATE INDEX k_node_kind IF NOT EXISTS",
        "FOR (n:KNode)",
        "ON (n.kind);",
        "",
    ]

    label_for_kind = {
        "T": "Topic",
        "L": "Lecture",
        "F": "File",
        "Fd": "File:Draft",
    }
    for node in sorted(migration.nodes.values(), key=lambda item: item.key):
        lines.extend(
            [
                f"MERGE (n:KNode {{key: {cypher_value(node.key)}}})",
                (
                    "SET "
                    f"n.local_id = {cypher_value(node.local_id)}, "
                    f"n.kind = {cypher_value(node.kind)}, "
                    f"n.title = {cypher_value(node.title)}, "
                    f"n.description = {cypher_value(node.description)}, "
                    f"n.research = {cypher_value(node.research)}, "
                    f"n.media_scenes = {cypher_value(node.media_scenes)}, "
                    f"n.media_videos = {cypher_value(node.media_videos)}"
                ),
                f"SET n:{label_for_kind[node.kind]};",
                "",
            ]
        )

    for edge in sorted(migration.groups, key=lambda item: (item.origin, item.position)):
        lines.extend(
            [
                (
                    f"MATCH (a:KNode {{key: {cypher_value(edge.origin)}}}), "
                    f"(b:KNode {{key: {cypher_value(edge.target)}}})"
                ),
                "MERGE (a)-[r:GROUPS]->(b)",
                f"SET r.position = {edge.position};",
                "",
            ]
        )

    for origin, target in sorted(migration.linear):
        lines.extend(
            [
                (
                    f"MATCH (a:KNode {{key: {cypher_value(origin)}}}), "
                    f"(b:KNode {{key: {cypher_value(target)}}})"
                ),
                "MERGE (a)-[:NEXT]->(b);",
                "",
            ]
        )

    for edge in sorted(
        migration.related,
        key=lambda item: (item.origin, item.target, item.weight or 0.0),
    ):
        lines.extend(
            [
                (
                    f"MATCH (a:KNode {{key: {cypher_value(edge.origin)}}}), "
                    f"(b:KNode {{key: {cypher_value(edge.target)}}})"
                ),
                "MERGE (a)-[r:RELATED_TO]->(b)",
            ]
        )
        if edge.weight is None:
            lines[-1] += ";"
        else:
            lines.extend([f"SET r.weight = {edge.weight};"])
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def print_report(migration: Migration) -> None:
    print(
        "directory graph: "
        f"{len(migration.nodes)} nodes, "
        f"{len(migration.groups)} GROUPS, "
        f"{len(migration.linear)} NEXT, "
        f"{len(migration.related)} RELATED_TO",
        file=sys.stderr,
    )
    for warning in migration.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in migration.errors:
        print(f"error: {error}", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Express the Directory Projection as Neo4j Cypher",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("."),
        help="k-graph repository root (default: current directory)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="write generated Cypher here; omit to validate only",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    migration = load_directory_graph(args.source)
    print_report(migration)
    if migration.errors:
        return 1

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(emit_cypher(migration), encoding="utf-8")
        print(f"wrote Cypher: {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
