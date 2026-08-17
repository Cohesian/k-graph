# Cohesian k-graph

`k-graph` is Cohesian's accepted knowledge registry. It defines knowledge as a
TLF graph, keeps a complete reviewable representation in Git, and provides an
equivalent Neo4j representation.

This repository is K's workspace: it owns the graph contract, documentation,
validation, projections, and operational tooling. `storage/local/` is the
current authoritative persistence. `storage/neo4j/` is a derived expression
that may be loaded into local Neo4j or Aura. A future K interface may operate
either persistence without changing the graph model.

Each knowledge node has a small intrinsic semantic surface:

```yaml
id: Immutable UUID
kind: T | L | F | Fd
title: Human-facing title
description: Concise meaning of this node
```

Its grouping, linear, and related connections are graph relationships. A
separate resource overlay records which accepted formats registered
contributors provide for it, categorized by contributor and domain. The
current contributors are `research` and `studio`.

## Read first

| Need | Read |
|---|---|
| Formal TLF model | [`docs/TLF.md`](docs/TLF.md) |
| Directory/YAML representation | [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) |
| Neo4j representation | [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) |
| Contributors | [`docs/CONTRIBUTORS.md`](docs/CONTRIBUTORS.md) |
| Resource overlay | [`docs/RESOURCE-OVERLAY.md`](docs/RESOURCE-OVERLAY.md) |
| Change proposals | [`docs/PROPOSALS.md`](docs/PROPOSALS.md) |
| Pending interfaces | [`docs/ROADMAP.md`](docs/ROADMAP.md) |
| Normative repository contract | [`CONTRACT.md`](CONTRACT.md) |
| Agent onboarding | [`AGENTS.md`](AGENTS.md) |

## Repository shape

```text
k-graph/
├── storage/
│   ├── local/         # complete authored graph in YAML
│   └── neo4j/         # schema and generated Cypher
├── tooling/           # validation and projection tooling
├── docs/              # model and representation documentation
├── k-graph.toml       # repository manifest
├── CONTRACT.md
├── AGENTS.md
└── README.md
```

The Local Directory Projection is currently authoritative. The generated
Cypher is derived from it and can be loaded into either local Neo4j or Aura.

Query identity is an immutable UUID `id` plus a rooted `path` derived from the
accepted grouping projection. Neo4j stores `id`; it derives `path` by following
`GROUPS` from `K`. Local storage derives the same address from its directory
tree. A query interface may use either selector or require both to agree.

## Current scope

Proposals and acceptance are manual. Contributor-specific storage remains
outside this registry manifest. The Directory and Neo4j projections are
domain-aware, and both Research and Studio expose the shared Tether protocol.
The Website may consume a Git snapshot of the Directory Projection before a
backend-agnostic K interface exists. Remote K persistence, content digests,
and automated contributor admission remain pending.
