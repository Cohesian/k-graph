#!/usr/bin/env python3
"""Express the local Directory Projection as Neo4j-readable Cypher.

The tool reads the complete directory/YAML k-graph, validates it, and emits a
reviewable property-graph expression. It never connects to Neo4j and never
modifies the Directory Projection.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kgraph_config import load_manifest, registered_contributors, storage_path

try:
    import yaml
    from yaml.constructor import ConstructorError
except ModuleNotFoundError:
    sys.exit("pyyaml is required: python -m pip install pyyaml")


KINDS = frozenset({"T", "L", "F", "Fd"})
COMPOSITES = frozenset({"T", "L"})
LEAVES = frozenset({"F", "Fd"})
NODE_FIELDS = frozenset(
    {"id", "title", "description", "kind", "contributions", "edges"}
)
EDGE_FIELDS = frozenset({"g", "l", "r"})
LINEAR_FIELDS = frozenset({"prev", "next"})
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
PROTOCOL_RE = re.compile(r"[a-z][a-z0-9-]*@[1-9][0-9]*")
SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class AcceptedResource:
    contributor: str
    hierarchy: tuple[str, ...]
    key: str
    protocol: str
    sha256: str


@dataclass
class Node:
    id: str
    path: str
    local_id: str
    kind: str
    title: str
    description: str
    source_path: Path
    parent_dir: Path
    contributions: list[AcceptedResource] = field(default_factory=list)
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
    registered_contributors: frozenset[str]
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


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_yaml(path: Path, graph: DirectoryGraph) -> dict[str, Any]:
    try:
        value = yaml.load(
            path.read_text(encoding="utf-8"),
            Loader=UniqueKeyLoader,
        ) or {}
    except (OSError, yaml.YAMLError) as exc:
        graph.error(path, f"cannot read YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        graph.error(path, "node YAML must be a mapping")
        return {}
    return value


def path_for_directory(tree_root: Path, directory: Path) -> str:
    relative = directory.relative_to(tree_root)
    return "K" if relative == Path(".") else relative.as_posix()


def path_for_leaf(tree_root: Path, leaf: Path) -> str:
    relative_parent = leaf.parent.relative_to(tree_root)
    return (
        leaf.stem
        if relative_parent == Path(".")
        else (relative_parent / leaf.stem).as_posix()
    )


def _typed_name(
    raw: object,
    prefix: str,
    *,
    path: Path,
    graph: DirectoryGraph,
) -> str | None:
    if not isinstance(raw, str) or not raw.startswith(prefix):
        graph.error(path, f"contribution key must start with {prefix!r}: {raw!r}")
        return None
    value = raw[len(prefix) :]
    if NAME_RE.fullmatch(value) is None:
        graph.error(path, f"invalid typed contribution key {raw!r}")
        return None
    return value


def _normalize_hierarchy(
    raw: dict[str, Any],
    *,
    contributor: str,
    prefix: tuple[str, ...],
    path: Path,
    graph: DirectoryGraph,
    out: list[AcceptedResource],
) -> None:
    for typed_key, value in raw.items():
        if isinstance(typed_key, str) and typed_key.startswith("h_"):
            segment = _typed_name(
                typed_key,
                "h_",
                path=path,
                graph=graph,
            )
            if segment is None:
                continue
            if not isinstance(value, dict) or not value:
                graph.error(path, f"{typed_key} must contain hierarchy or resources")
                continue
            _normalize_hierarchy(
                value,
                contributor=contributor,
                prefix=(*prefix, segment),
                path=path,
                graph=graph,
                out=out,
            )
            continue

        if isinstance(typed_key, str) and typed_key.startswith("r_"):
            key = _typed_name(
                typed_key,
                "r_",
                path=path,
                graph=graph,
            )
            if key is None:
                continue
            if not prefix:
                graph.error(path, f"{typed_key} requires at least one h_ segment")
                continue
            if not isinstance(value, dict):
                graph.error(path, f"{typed_key} must map to protocol and sha256")
                continue
            unknown = sorted(set(value) - {"protocol", "sha256"})
            if unknown:
                graph.error(
                    path,
                    f"{typed_key} has unsupported fields: {', '.join(unknown)}",
                )
            protocol = value.get("protocol")
            sha256 = value.get("sha256")
            if not isinstance(protocol, str) or PROTOCOL_RE.fullmatch(protocol) is None:
                graph.error(path, f"{typed_key}.protocol is not a versioned protocol id")
                continue
            if not isinstance(sha256, str) or SHA256_RE.fullmatch(sha256) is None:
                graph.error(path, f"{typed_key}.sha256 must be lowercase SHA-256")
                continue
            out.append(
                AcceptedResource(
                    contributor=contributor,
                    hierarchy=prefix,
                    key=key,
                    protocol=protocol,
                    sha256=sha256,
                )
            )
            continue

        graph.error(path, f"contribution key must start with 'h_' or 'r_': {typed_key!r}")


def normalize_contributions(
    raw: dict[str, Any],
    *,
    path: Path,
    graph: DirectoryGraph,
) -> list[AcceptedResource]:
    raw_contributions = raw.get("contributions", {})
    if not isinstance(raw_contributions, dict):
        graph.error(path, "contributions must be a mapping")
        return []

    out: list[AcceptedResource] = []
    for typed_contributor, hierarchy in raw_contributions.items():
        contributor = _typed_name(
            typed_contributor,
            "c_",
            path=path,
            graph=graph,
        )
        if contributor is None:
            continue
        if contributor not in graph.registered_contributors:
            graph.error(path, f"unknown contributor {contributor!r}")
            continue
        if not isinstance(hierarchy, dict) or not hierarchy:
            graph.error(path, f"{typed_contributor} must contain hierarchy entries")
            continue
        _normalize_hierarchy(
            hierarchy,
            contributor=contributor,
            prefix=(),
            path=path,
            graph=graph,
            out=out,
        )
    return out


def add_node(
    graph: DirectoryGraph,
    *,
    node_path: str,
    local_id: str,
    path: Path,
    parent_dir: Path,
    raw: dict[str, Any],
    allowed_kinds: frozenset[str],
) -> None:
    for field_name in sorted(set(raw) - NODE_FIELDS):
        graph.error(path, f"unknown node field {field_name!r}")

    raw_id = raw.get("id")
    try:
        parsed_id = uuid.UUID(raw_id) if isinstance(raw_id, str) else None
    except ValueError:
        parsed_id = None
    node_id = str(parsed_id) if parsed_id is not None else ""
    if not node_id or node_id != raw_id or parsed_id.version != 4:
        graph.error(path, "id must be a canonical UUIDv4")
        return

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

    if node_path in graph.nodes:
        graph.error(path, f"duplicate graph path {node_path!r}")
        return
    if any(node.id == node_id for node in graph.nodes.values()):
        graph.error(path, f"duplicate node id {node_id!r}")
        return

    contributions = normalize_contributions(
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

    graph.nodes[node_path] = Node(
        id=node_id,
        path=node_path,
        local_id=local_id,
        kind=kind,
        title=title.strip(),
        description=description.strip(),
        source_path=path,
        parent_dir=parent_dir,
        contributions=contributions,
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
            node_path=path_for_directory(tree_root, directory),
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
                node_path=path_for_leaf(tree_root, leaf),
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
        if node.path == parent_key:
            continue
        if node.kind in COMPOSITES and node.source_path.parent.parent == directory:
            children[node.local_id] = node.path
        elif node.kind in LEAVES and node.source_path.parent == directory:
            children[node.local_id] = node.path
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
            out[candidate.local_id] = candidate.path
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
            f"{edge_name} target {target!r} is neither a rooted path nor a sibling id",
        )
    return key


def build_group_edges(graph: DirectoryGraph) -> None:
    for node in graph.nodes.values():
        if node.kind not in COMPOSITES:
            continue
        available = child_nodes(graph, node.path)
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
            graph.groups.append(GroupEdge(node.path, target, position))

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
        declared_prev[node.path] = resolve_local_target(
            graph,
            node,
            linear.get("prev"),
            edge_name="edges.l.prev",
        )
        declared_next[node.path] = resolve_local_target(
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
                graph.related.append(RelatedEdge(node.path, target, weight))


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
        tree_root = storage_path(source_root, manifest, "local")
        contributors = registered_contributors(manifest)
    except (OSError, ValueError) as exc:
        graph = DirectoryGraph(
            source_root=source_root,
            tree_root=source_root / "storage" / "directory",
            registered_contributors=frozenset(),
        )
        graph.errors.append(f"k-graph.toml: {exc}")
        return graph

    graph = DirectoryGraph(
        source_root=source_root,
        tree_root=tree_root,
        registered_contributors=contributors,
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
        "DROP CONSTRAINT k_node_path IF EXISTS;",
        "",
        "CREATE CONSTRAINT k_node_id IF NOT EXISTS",
        "FOR (n:KNode)",
        "REQUIRE n.id IS UNIQUE;",
        "",
        "CREATE INDEX k_node_kind IF NOT EXISTS",
        "FOR (n:KNode)",
        "ON (n.kind);",
        "",
        "CREATE CONSTRAINT contributor_id IF NOT EXISTS",
        "FOR (c:Contributor)",
        "REQUIRE c.id IS UNIQUE;",
        "",
        "MATCH (:Contributor)-[r:CONTRIBUTED]->(:KNode)",
        "DELETE r;",
        "",
        "MATCH (:Contributor)-[r:PROVIDES]->(:KNode)",
        "DELETE r;",
        "",
        "MATCH (n:KNode)",
        "REMOVE n.path;",
        "",
    ]

    label_for_kind = {
        "T": "Topic",
        "L": "Lecture",
        "F": "File",
        "Fd": "File:Draft",
    }
    for node in sorted(graph.nodes.values(), key=lambda item: item.path):
        lines.extend(
            [
                f"MERGE (n:KNode {{id: {cypher_value(node.id)}}})",
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

    for contributor in sorted(graph.registered_contributors):
        lines.extend(
            [
                f"MERGE (:Contributor {{id: {cypher_value(contributor)}}});",
                "",
            ]
        )

    for node in sorted(graph.nodes.values(), key=lambda item: item.path):
        for resource in sorted(
            node.contributions,
            key=lambda item: (item.contributor, item.hierarchy, item.key),
        ):
            lines.extend(
                [
                    (
                        f"MATCH (c:Contributor {{id: {cypher_value(resource.contributor)}}}), "
                        f"(n:KNode {{id: {cypher_value(node.id)}}})"
                    ),
                    (
                        "MERGE (c)-[r:PROVIDES {"
                        f"hierarchy: {cypher_value(list(resource.hierarchy))}, "
                        f"key: {cypher_value(resource.key)}"
                        "}]->(n)"
                    ),
                    (
                        "SET "
                        f"r.protocol = {cypher_value(resource.protocol)}, "
                        f"r.sha256 = {cypher_value(resource.sha256)};"
                    ),
                    "",
                ]
            )

    for edge in sorted(graph.groups, key=lambda item: (item.origin, item.position)):
        origin_id = graph.nodes[edge.origin].id
        target_id = graph.nodes[edge.target].id
        lines.extend(
            [
                (
                    f"MATCH (a:KNode {{id: {cypher_value(origin_id)}}}), "
                    f"(b:KNode {{id: {cypher_value(target_id)}}})"
                ),
                "MERGE (a)-[r:GROUPS]->(b)",
                f"SET r.position = {edge.position};",
                "",
            ]
        )

    for origin, target in sorted(graph.linear):
        origin_id = graph.nodes[origin].id
        target_id = graph.nodes[target].id
        lines.extend(
            [
                (
                    f"MATCH (a:KNode {{id: {cypher_value(origin_id)}}}), "
                    f"(b:KNode {{id: {cypher_value(target_id)}}})"
                ),
                "MERGE (a)-[:NEXT]->(b);",
                "",
            ]
        )

    for edge in sorted(
        graph.related,
        key=lambda item: (item.origin, item.target, item.weight or 0.0),
    ):
        origin_id = graph.nodes[edge.origin].id
        target_id = graph.nodes[edge.target].id
        lines.extend(
            [
                (
                    f"MATCH (a:KNode {{id: {cypher_value(origin_id)}}}), "
                    f"(b:KNode {{id: {cypher_value(target_id)}}})"
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
    resources = sum(len(node.contributions) for node in graph.nodes.values())
    print(
        "directory graph: "
        f"{len(graph.nodes)} nodes, "
        f"{len(graph.groups)} GROUPS, "
        f"{len(graph.linear)} NEXT, "
        f"{len(graph.related)} RELATED_TO, "
        f"{resources} RESOURCES",
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
