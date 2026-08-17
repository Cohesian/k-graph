# Cohesian k-graph — agent onboarding

## Purpose

This workspace maintains Cohesian's accepted TLF knowledge graph: node
identity, intrinsic semantics, graph topology, accepted resources, and
equivalent graph representations.

Work here as the keeper of a small, coherent registry. Read the current graph,
help shape proposals, apply accepted changes, and verify that every
representation still describes the same object.

## Read first

| Need | Read |
|---|---|
| Repository overview | [`README.md`](README.md) |
| Formal model | [`docs/TLF.md`](docs/TLF.md) |
| Normative contract | [`CONTRACT.md`](CONTRACT.md) |
| Directory representation | [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) |
| Neo4j representation | [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) |
| Contributor model | [`docs/CONTRIBUTORS.md`](docs/CONTRIBUTORS.md) |
| Resource overlay | [`docs/RESOURCE-OVERLAY.md`](docs/RESOURCE-OVERLAY.md) |
| Proposal model | [`docs/PROPOSALS.md`](docs/PROPOSALS.md) |
| Pending interfaces | [`docs/ROADMAP.md`](docs/ROADMAP.md) |
| Tooling | [`tooling/README.md`](tooling/README.md) |

## Working model

A Directory node looks like:

```yaml
title: Function
description: Functions as bounded nodes and transformations.
kind: F
id: 42292902-3874-4d54-87ec-0e1b7362af13
contributors:
  research:
    documents:
      - md
edges:
  g: []
  l:
    prev: null
    next: null
  r: []
```

The intrinsic fields describe the node. `edges` expresses its local graph
neighborhood. `contributors` expresses accepted resources by contributor,
domain, and format.

Preserve these invariants when changing the graph:

- the root is `K`, represented as a `T`;
- each node has an immutable, unique UUID `id`;
- each node has one rooted `path` derived from the accepted grouping
  projection;
- `g`, `l`, and `r` remain distinct edge families;
- `GROUPS.position` preserves authored child order;
- Neo4j derives rooted paths through `GROUPS` rather than persisting them as
  node properties;
- contributor ids, domains, and formats are registered in `k-graph.toml`;
- the Directory and Neo4j representations remain equivalent; and
- generated Cypher is regenerated through the tooling.

## Validation

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ./tooling
.venv/bin/kgraph-validate
.venv/bin/kgraph-to-neo4j --out storage/neo4j/k-graph.cypher
git diff --check
```

Graph validation errors are blocking.
