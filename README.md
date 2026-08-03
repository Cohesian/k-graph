# Cohesian k-graph

`k-graph` is Cohesian's accepted knowledge registry. It defines knowledge as a
TLF graph, keeps a complete reviewable representation in Git, and provides an
equivalent Neo4j representation.

Each knowledge node has a small intrinsic semantic surface:

```yaml
kind: T | L | F | Fd
title: Human-facing title
description: Concise meaning of this node
```

Its grouping, linear, and related connections are graph relationships. A
separate contributor overlay records which registered contributors introduced
the node or supplied content forms for it. The current contributors are
`research` and `studio`.

## Read first

| Need | Read |
|---|---|
| Formal TLF model | [`docs/TLF.md`](docs/TLF.md) |
| Directory/YAML representation | [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) |
| Neo4j representation | [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) |
| Contributors | [`docs/CONTRIBUTORS.md`](docs/CONTRIBUTORS.md) |
| Change proposals | [`docs/PROPOSALS.md`](docs/PROPOSALS.md) |
| Pending interfaces | [`docs/ROADMAP.md`](docs/ROADMAP.md) |
| Normative repository contract | [`CONTRACT.md`](CONTRACT.md) |
| Agent onboarding | [`AGENTS.md`](AGENTS.md) |

## Repository shape

```text
k-graph/
├── representations/
│   ├── directory/     # complete authored graph in YAML
│   └── neo4j/         # schema and generated Cypher
├── tooling/           # validation and projection tooling
├── docs/              # model and representation documentation
├── k-graph.toml       # repository manifest
├── CONTRACT.md
├── AGENTS.md
└── README.md
```

The Directory Projection is currently authoritative. The generated Cypher is
derived from it and can be loaded into either local Neo4j or Aura.

The target query identity is an immutable node `id` plus a rooted `path`
derived from the accepted grouping projection. The present Neo4j `key`
property is the current serialization of that path; stable ids remain a
pending materialization step.

## Current scope

Proposals and acceptance are manual. Contributor-specific storage and content
resolution will be exposed by contributor interfaces later; they are not part
of this registry manifest.
