# k-graph contract

Version: **0.5.0**

Status: **draft**

## 1. Purpose

The k-graph is Cohesian's accepted knowledge registry. It provides stable
knowledge-node identity, intrinsic node semantics, explicit topology, and
contributor attribution without embedding contributed content bodies.

The distinguished root is `K`, a Topic.

## 2. Authorities

| Concern | Authority |
|---|---|
| Mathematical model | [`docs/TLF.md`](docs/TLF.md) |
| Authored graph | [`storage/local/`](storage/local/) |
| Neo4j expression | [`storage/neo4j/`](storage/neo4j/) |
| Storage and contributor registry | [`k-graph.toml`](k-graph.toml) |

Translation must preserve node identity and semantics, the `g`, `l`, and `r`
edge families, and contributor attribution.

## 3. Node semantics

Every node has:

```yaml
id: 42292902-3874-4d54-87ec-0e1b7362af13
kind: T | L | F | Fd
title: Human-facing title
description: Concise local description
```

`kind` is a semantic property even when a concrete representation can derive
it. The current Directory Projection stores it explicitly. `title` and
`description` identify and explain the knowledge node; they are not the full
research or media body.

Kinds are:

| Kind | Meaning |
|---|---|
| `T` | Topic composite |
| `L` | Lecture composite |
| `F` | File leaf |
| `Fd` | Draft File leaf |

`Fd` is a flat kind with the same graph capabilities as `F`.

The identity model has two selectors:

| Selector | Meaning |
|---|---|
| `id` | Immutable identity, stable across graph revisions and moves |
| `path` | Root-derived address in one accepted `g` projection |

`path` is unique inside a graph revision but may change when grouping is
reorganized. `id` remains fixed. A query may provide either selector; when it
provides both, they must resolve to the same node.

K currently materializes `id` as a canonical UUIDv4 in every Directory node
and as a unique Neo4j property. Neo4j internal element ids are never portable
identity.

`path` is derived, not persisted as a Neo4j node property. The Local Directory
Projection derives it from containment; Neo4j derives it from the unique
`GROUPS` route starting at `K`. A later cache may materialize paths as derived
data without making them authoritative.

## 4. Topology

Topology is represented by three disjoint edge families:

| Axis | Neo4j expression | Meaning |
|---|---|---|
| `g` | `GROUPS {position}` | Structural grouping and authored order |
| `l` | `NEXT` | Linear traversal; reverse traversal is `prev` |
| `r` | `RELATED_TO {weight?}` | Directed, optional weighted relation |

The `g` projection is a rooted ordered tree and therefore a DAG. Every
non-root node has exactly one grouping parent. Only `T` and `L` may group
children.

Each node has at most one incoming and one outgoing `NEXT`. A single physical
relationship represents both `prev` and `next`; linear components are acyclic
in this contract.

`RELATED_TO` may connect any kinds, fan out, and form cycles. Its weight is
optional and currently has no universal scale.

## 5. Contributor overlay

The registered contributor set is:

```text
research
studio
```

A contributor relation records participation in a node. Its format list says
which content forms that contributor supplied:

```yaml
contributors:
  research:
    - md
  studio:
    - py
    - mp4
```

An empty format list is meaningful: the contributor introduced or shaped the
knowledge node without attaching a content form.

Contributor relations do not change TLF kind or topology. Exact change-level
provenance belongs to a future accepted-proposal history; the node relation is
the current compact attribution view. The full model is in
[`docs/CONTRIBUTORS.md`](docs/CONTRIBUTORS.md).

## 6. Proposals

Registered contributors may asynchronously propose node or relationship
creation, replacement, patching, or deletion against a known graph revision.
The combined candidate graph is validated and accepted or rejected atomically.

The current workflow is manual. Its conceptual envelope and validation stages
are described in [`docs/PROPOSALS.md`](docs/PROPOSALS.md).

## 7. Representation contract

The repository manifest names the authoritative storage, the available
projections, and the allowed contributor formats. It contains no credentials,
machine-specific paths, external repository locations, or content URLs.

The Directory and Neo4j documents define how the same model is expressed:

- [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md)
- [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md)

Generated Neo4j Cypher is derived and is regenerated through the repository
tooling.
