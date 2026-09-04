# Cohesian k-graph

`k-graph` is Cohesian's accepted knowledge registry. It defines knowledge as a
TLE graph, keeps a complete reviewable representation in Git, and provides an
equivalent Neo4j representation.

This repository is K's workspace: it owns the graph contract, documentation,
validation, projections, and operational tooling. `storage/local/` is the
current authoritative persistence. `storage/neo4j/` is a derived expression
that may be loaded into local Neo4j or Aura. A future K interface may operate
either persistence without changing the graph model.

Each knowledge node has a small intrinsic semantic surface:

```yaml
id: Immutable UUID
kind: T | L | E | Ed
title: Human-facing title
description: Concise meaning of this node
```

Its grouping, linear, and related connections are graph relationships. A
separate resource overlay records accepted contributor resources by hierarchy
and key. Each accepted resource names a versioned protocol and canonical
SHA-256 digest. The current registered contributor is `research`. Studio may
produce media recorded with `produced_by = "studio"`, but Research owns the
accepted resource and its locations.

## Read first

| Need | Read |
|---|---|
| Formal TLE model | [`docs/TLE.md`](docs/TLE.md) |
| Directory/YAML representation | [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) |
| Neo4j representation | [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) |
| Contributors | [`docs/CONTRIBUTORS.md`](docs/CONTRIBUTORS.md) |
| Resource overlay | [`docs/RESOURCE-OVERLAY.md`](docs/RESOURCE-OVERLAY.md) |
| Resource contract | [`docs/RESOURCE-CONTRACT-V2.md`](docs/RESOURCE-CONTRACT-V2.md) |
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

Proposals and acceptance are manual. Contributor bytes, stores, credentials,
and physical locations remain outside K. The Directory and Neo4j projections
preserve the same accepted resource records, and Tether validates those
records against contributor inventories. The Website may consume a Git
snapshot of the Directory Projection before a backend-agnostic K interface
exists. Remote K persistence and automated contributor admission remain
pending.
