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
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kgraph_config import contributor_formats, load_manifest, representation_path

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("pyyaml is required: python -m pip install pyyaml")


KINDS = frozenset({"T", "L", "F", "Fd"})
COMPOSITES = frozenset({"T", "L"})
LEAVES = frozenset({"F", "Fd"})
NODE_FIELDS = frozenset({"title", "description", "kind", "contributors", "edges"})
EDGE_FIELDS = frozenset({"g", "l", "r"})
LINEAR_FIELDS = frozenset({"prev", "next"})


@dataclass
class Node:
    key: str
    local_id: str
    kind: str
    title: str
    description: str
    source_path: Path
    parent_dir: Path
    contributors: dict[str, list[str]] = field(default_factory=dict)
    edges: dict[str, Any] = field(default_factory=dict)


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
class DirectoryGraph:
    source_root: Path
    tree_root: Path
    contributor_formats: dict[str, frozenset[str]]
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


def load_yaml(path: Path, graph: DirectoryGraph) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        graph.error(path, f"cannot read YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        graph.error(path, "node YAML must be a mapping")
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


def normalize_contributors(
    raw: dict[str, Any],
    *,
    path: Path,
    graph: DirectoryGraph,
) -> dict[str, list[str]]:
    raw_contributors = raw.get("contributors", {})
    if not isinstance(raw_contributors, dict):
        graph.error(path, "contributors must be a mapping")
        return {}

    out: dict[str, list[str]] = {}
    for contributor, raw_formats in raw_contributors.items():
        allowed = graph.contributor_formats.get(contributor)
        if allowed is None:
            graph.error(path, f"unknown contributor {contributor!r}")
            continue
        if not isinstance(raw_formats, list):
            graph.error(path, f"contributors.{contributor} must be a list")
        formats = unique_strings(as_list(raw_formats))
        if len(formats) != len(as_list(raw_formats)):
            graph.error(
                path,
                f"contributors.{contributor} must contain unique strings",
            )
        for value in formats:
            if value not in allowed:
                graph.error(
                    path,
                    f"contributor {contributor!r} does not accept format {value!r}",
                )
        out[contributor] = formats
    return out


def add_node(
    graph: DirectoryGraph,
    *,
    key: str,
    local_id: str,
    path: Path,
    parent_dir: Path,
    raw: dict[str, Any],
    allowed_kinds: frozenset[str],
) -> None:
    for field_name in sorted(set(raw) - NODE_FIELDS):
        graph.error(path, f"unknown node field {field_name!r}")

    kind = raw.get("kind")
    if kind not in allowed_kinds:
        graph.error(
            path,
            f"kind must be one of {sorted(allowed_kinds)}, got {kind!r}",
        )
        return

    expected_kind = "T" if local_id == "K" else local_id.split("-", 1)[0]
    if kind != expected_kind:
        graph.error(
            path,
            f"kind {kind!r} does not match local id prefix {expected_kind!r}",
        )

    title = raw.get("title")
    description = raw.get("description")
    if not isinstance(title, str) or not title.strip():
        graph.error(path, "title must be a non-empty string")
        title = ""
    if not isinstance(description, str) or not description.strip():
        graph.error(path, "description must be a non-empty string")
        description = ""

    if key in graph.nodes:
        graph.error(path, f"duplicate graph key {key!r}")
        return

    contributors = normalize_contributors(
        raw,
        path=path,
        graph=graph,
    )
    edges = raw.get("edges") or {}
    if not isinstance(edges, dict):
        graph.error(path, "edges must be a mapping")
        edges = {}
    for field_name in sorted(set(edges) - EDGE_FIELDS):
        graph.error(path, f"unknown edge family {field_name!r}")

    raw_group = edges.get("g", [])
    if not isinstance(raw_group, list):
        graph.error(path, "edges.g must be a list")
    elif kind in LEAVES and raw_group:
        graph.error(path, "File nodes cannot group children")

    raw_linear = edges.get("l", {})
    if not isinstance(raw_linear, dict):
        graph.error(path, "edges.l must be a mapping")
    else:
        for field_name in sorted(set(raw_linear) - LINEAR_FIELDS):
            graph.error(path, f"unknown linear field {field_name!r}")

    if not isinstance(edges.get("r", []), list):
        graph.error(path, "edges.r must be a list")

    graph.nodes[key] = Node(
        key=key,
        local_id=local_id,
        kind=kind,
        title=title.strip(),
        description=description.strip(),
        source_path=path,
        parent_dir=parent_dir,
        contributors=contributors,
        edges=edges,
    )


def discover_nodes(graph: DirectoryGraph) -> None:
    tree_root = graph.tree_root
    if not tree_root.is_dir():
        graph.errors.append(f"k-graph directory not found: {tree_root}")
        return

    directories = [tree_root, *sorted(path for path in tree_root.rglob("*") if path.is_dir())]
    for directory in directories:
        props = directory / "props.yaml"
        if not props.exists():
            graph.error(directory, "composite directory has no props.yaml")
            continue
        raw = load_yaml(props, graph)
        add_node(
            graph,
            key=key_for_directory(tree_root, directory),
            local_id="K" if directory == tree_root else directory.name,
            path=props,
            parent_dir=directory.parent,
            raw=raw,
            allowed_kinds=COMPOSITES,
        )

        for leaf in sorted(directory.glob("*.yaml")):
            if leaf.name == "props.yaml":
                continue
            raw_leaf = load_yaml(leaf, graph)
            add_node(
                graph,
                key=key_for_leaf(tree_root, leaf),
                local_id=leaf.stem,
                path=leaf,
                parent_dir=directory,
                raw=raw_leaf,
                allowed_kinds=LEAVES,
            )


def child_nodes(graph: DirectoryGraph, parent_key: str) -> dict[str, str]:
    parent = graph.nodes[parent_key]
    directory = parent.source_path.parent
    children: dict[str, str] = {}
    for node in graph.nodes.values():
        if node.key == parent_key:
            continue
        if node.kind in COMPOSITES and node.source_path.parent.parent == directory:
            children[node.local_id] = node.key
        elif node.kind in LEAVES and node.source_path.parent == directory:
            children[node.local_id] = node.key
    return children


def siblings(graph: DirectoryGraph, node: Node) -> dict[str, str]:
    directory = node.source_path.parent if node.kind in LEAVES else node.source_path.parent.parent
    out: dict[str, str] = {}
    for candidate in graph.nodes.values():
        candidate_directory = (
            candidate.source_path.parent
            if candidate.kind in LEAVES
            else candidate.source_path.parent.parent
        )
        if candidate_directory == directory:
            out[candidate.local_id] = candidate.key
    return out


def resolve_local_target(
    graph: DirectoryGraph,
    node: Node,
    target: Any,
    *,
    edge_name: str,
) -> str | None:
    if target is None:
        return None
    if not isinstance(target, str) or not target:
        graph.error(node.source_path, f"{edge_name} target must be a non-empty string")
        return None
    key = graph.nodes.get(target) and target
    if key is None:
        key = siblings(graph, node).get(target)
    if key is None:
        graph.error(
            node.source_path,
            f"{edge_name} target {target!r} is neither a portable key nor a sibling id",
        )
    return key


def build_group_edges(graph: DirectoryGraph) -> None:
    for node in graph.nodes.values():
        if node.kind not in COMPOSITES:
            continue
        available = child_nodes(graph, node.key)
        raw_group = as_list(node.edges.get("g"))
        seen: set[str] = set()
        for position, child_id in enumerate(raw_group):
            if not isinstance(child_id, str) or not child_id:
                graph.error(node.source_path, "edges.g entries must be non-empty strings")
                continue
            target = available.get(child_id)
            if target is None:
                graph.error(
                    node.source_path,
                    f"edges.g child {child_id!r} is not an immediate directory child",
                )
                continue
            if child_id in seen:
                graph.error(node.source_path, f"edges.g repeats child {child_id!r}")
                continue
            seen.add(child_id)
            graph.groups.append(GroupEdge(node.key, target, position))

        unlisted = sorted(set(available) - seen)
        for child_id in unlisted:
            graph.error(
                node.source_path,
                f"immediate child {child_id!r} is absent from edges.g",
            )


def build_linear_edges(graph: DirectoryGraph) -> None:
    declared_prev: dict[str, str | None] = {}
    declared_next: dict[str, str | None] = {}

    for node in graph.nodes.values():
        linear = node.edges.get("l") or {}
        if not isinstance(linear, dict):
            graph.error(node.source_path, "edges.l must be a mapping")
            continue
        declared_prev[node.key] = resolve_local_target(
            graph,
            node,
            linear.get("prev"),
            edge_name="edges.l.prev",
        )
        declared_next[node.key] = resolve_local_target(
            graph,
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
            graph.error(
                graph.nodes[target].source_path,
                f"prev points to {graph.nodes[origin].local_id!r}, but its next is not reciprocal",
            )
        if declared_prev.get(target) != origin:
            graph.error(
                graph.nodes[origin].source_path,
                f"next points to {graph.nodes[target].local_id!r}, but its prev is not reciprocal",
            )

    outgoing = Counter(origin for origin, _ in claims)
    incoming = Counter(target for _, target in claims)
    for key, count in outgoing.items():
        if count > 1:
            graph.error(graph.nodes[key].source_path, "more than one outgoing NEXT")
    for key, count in incoming.items():
        if count > 1:
            graph.error(graph.nodes[key].source_path, "more than one incoming NEXT")

    graph.linear = claims

    next_by_origin = dict(claims)
    for start in graph.nodes:
        seen: set[str] = set()
        current = start
        while current in next_by_origin:
            if current in seen:
                graph.error(graph.nodes[current].source_path, "linear cycle detected")
                break
            seen.add(current)
            current = next_by_origin[current]


def build_related_edges(graph: DirectoryGraph) -> None:
    for node in graph.nodes.values():
        for entry in as_list(node.edges.get("r")):
            weight: float | None = None
            target_value = entry
            if isinstance(entry, dict):
                target_value = entry.get("target")
                raw_weight = entry.get("weight")
                if raw_weight is not None:
                    if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
                        graph.error(node.source_path, "edges.r weight must be numeric")
                        continue
                    weight = float(raw_weight)
            target = resolve_local_target(
                graph,
                node,
                target_value,
                edge_name="edges.r",
            )
            if target is not None:
                graph.related.append(RelatedEdge(node.key, target, weight))


def validate_graph(graph: DirectoryGraph) -> None:
    if "K" not in graph.nodes:
        graph.errors.append("distinguished root K was not discovered")
        return

    incoming = Counter(edge.target for edge in graph.groups)
    if incoming["K"]:
        graph.error(graph.nodes["K"].source_path, "K must not have a grouping parent")
    for key, node in graph.nodes.items():
        expected = 0 if key == "K" else 1
        if incoming[key] != expected:
            graph.error(
                node.source_path,
                f"expected {expected} grouping parent(s), found {incoming[key]}",
            )

    adjacency: dict[str, list[str]] = {key: [] for key in graph.nodes}
    for edge in graph.groups:
        adjacency[edge.origin].append(edge.target)

    state: dict[str, int] = {}

    def visit(key: str) -> None:
        marker = state.get(key, 0)
        if marker == 1:
            graph.error(graph.nodes[key].source_path, "grouping cycle detected")
            return
        if marker == 2:
            return
        state[key] = 1
        for child in adjacency[key]:
            visit(child)
        state[key] = 2

    visit("K")
    unreachable = sorted(set(graph.nodes) - set(state))
    for key in unreachable:
        graph.error(graph.nodes[key].source_path, "node is not reachable from K")


def load_directory_graph(source_root: Path) -> DirectoryGraph:
    source_root = source_root.resolve()
    try:
        manifest = load_manifest(source_root)
        tree_root = representation_path(source_root, manifest, "directory")
        formats = contributor_formats(manifest)
    except (OSError, ValueError) as exc:
        graph = DirectoryGraph(
            source_root=source_root,
            tree_root=source_root / "representations" / "directory",
            contributor_formats={},
        )
        graph.errors.append(f"k-graph.toml: {exc}")
        return graph

    graph = DirectoryGraph(
        source_root=source_root,
        tree_root=tree_root,
        contributor_formats=formats,
    )
    discover_nodes(graph)
    if graph.nodes:
        build_group_edges(graph)
        build_linear_edges(graph)
        build_related_edges(graph)
        validate_graph(graph)
    return graph


def cypher_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def emit_cypher(graph: DirectoryGraph) -> str:
    lines = [
        "// Generated by tooling/to_neo4j.py.",
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
        "CREATE CONSTRAINT contributor_id IF NOT EXISTS",
        "FOR (c:Contributor)",
        "REQUIRE c.id IS UNIQUE;",
        "",
    ]

    label_for_kind = {
        "T": "Topic",
        "L": "Lecture",
        "F": "File",
        "Fd": "File:Draft",
    }
    for node in sorted(graph.nodes.values(), key=lambda item: item.key):
        lines.extend(
            [
                f"MERGE (n:KNode {{key: {cypher_value(node.key)}}})",
                (
                    "SET "
                    f"n.local_id = {cypher_value(node.local_id)}, "
                    f"n.kind = {cypher_value(node.kind)}, "
                    f"n.title = {cypher_value(node.title)}, "
                    f"n.description = {cypher_value(node.description)}"
                ),
                f"SET n:{label_for_kind[node.kind]};",
                "",
            ]
        )

    for contributor in sorted(graph.contributor_formats):
        lines.extend(
            [
                f"MERGE (:Contributor {{id: {cypher_value(contributor)}}});",
                "",
            ]
        )

    for node in sorted(graph.nodes.values(), key=lambda item: item.key):
        for contributor, formats in sorted(node.contributors.items()):
            lines.extend(
                [
                    (
                        f"MATCH (c:Contributor {{id: {cypher_value(contributor)}}}), "
                        f"(n:KNode {{key: {cypher_value(node.key)}}})"
                    ),
                    "MERGE (c)-[r:CONTRIBUTED]->(n)",
                    f"SET r.formats = {cypher_value(formats)};",
                    "",
                ]
            )

    for edge in sorted(graph.groups, key=lambda item: (item.origin, item.position)):
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

    for origin, target in sorted(graph.linear):
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
        graph.related,
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


def print_report(graph: DirectoryGraph) -> None:
    contributions = sum(len(node.contributors) for node in graph.nodes.values())
    print(
        "directory graph: "
        f"{len(graph.nodes)} nodes, "
        f"{len(graph.groups)} GROUPS, "
        f"{len(graph.linear)} NEXT, "
        f"{len(graph.related)} RELATED_TO, "
        f"{contributions} CONTRIBUTED",
        file=sys.stderr,
    )
    for warning in graph.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in graph.errors:
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
    graph = load_directory_graph(args.source)
    print_report(graph)
    if graph.errors:
        return 1

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(emit_cypher(graph), encoding="utf-8")
        print(f"wrote Cypher: {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
