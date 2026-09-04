# Cohesian k-graph — agent onboarding

## Purpose

This workspace maintains Cohesian's accepted TLE knowledge graph: node
identity, intrinsic semantics, graph topology, accepted resources, and
equivalent graph representations.

Work here as the keeper of a small, coherent registry. Read the current graph,
help shape proposals, apply accepted changes, and verify that every
representation still describes the same object.

## Read first

| Need | Read |
|---|---|
| Repository overview | [`README.md`](README.md) |
| Formal model | [`docs/TLE.md`](docs/TLE.md) |
| Normative contract | [`CONTRACT.md`](CONTRACT.md) |
| Directory representation | [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) |
| Neo4j representation | [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) |
| Contributor model | [`docs/CONTRIBUTORS.md`](docs/CONTRIBUTORS.md) |
| Resource overlay | [`docs/RESOURCE-OVERLAY.md`](docs/RESOURCE-OVERLAY.md) |
| Resource contract | [`docs/RESOURCE-CONTRACT-V2.md`](docs/RESOURCE-CONTRACT-V2.md) |
| Proposal model | [`docs/PROPOSALS.md`](docs/PROPOSALS.md) |
| Pending interfaces | [`docs/ROADMAP.md`](docs/ROADMAP.md) |
| Tooling | [`tooling/README.md`](tooling/README.md) |

## Working model

A Directory node looks like:

```yaml
title: Functions
description: One lens on functions as bounded executable nodes.
kind: E
id: 499ff1af-eed7-425d-9fed-e357ec2e0b97
contributions:
  c_research:
    h_documents:
      r_md:
        protocol: markdown-file@1
        sha256: aaacecaa42528397cc3cca3c88141863d7f381a50bec28bdacf6492dc1472386
edges:
  g: []
  l:
    prev: null
    next: null
  r: []
```

The intrinsic fields describe the node. `edges` expresses its local graph
neighborhood. `contributions` records accepted resources by contributor,
hierarchy, and resource key. Each accepted leaf carries the protocol that
defines its shape and the canonical SHA-256 of its accepted bytes.

Preserve these invariants when changing the graph:

- the root is `K`, represented as a `T`;
- each node has an immutable, unique UUID `id`;
- each node has one rooted `path` derived from the accepted grouping
  projection;
- `g`, `l`, and `r` remain distinct edge families;
- `GROUPS.position` preserves authored child order;
- Neo4j derives rooted paths through `GROUPS` rather than persisting them as
  node properties;
- every `c_` key names a contributor registered in `k-graph.toml`;
- `h_` keys form a non-empty hierarchy of arbitrary depth;
- every `r_` key is unique inside one `(node, contributor, hierarchy)`
  namespace and carries exactly `protocol` and `sha256`;
- K stores acceptance metadata, while contributors retain locations and bytes;
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
