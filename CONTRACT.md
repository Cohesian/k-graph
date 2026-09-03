# k-graph contract

Version: **0.6.0**

Status: **draft**

## 1. Purpose

The k-graph is Cohesian's accepted knowledge registry. It provides stable
knowledge-node identity, intrinsic node semantics, explicit topology, and
accepted contributor resources without embedding contributed content bodies.

The distinguished root is `K`, a Topic.

## 2. Authorities

| Concern | Authority |
|---|---|
| Mathematical model | [`docs/TLF.md`](docs/TLF.md) |
| Resource overlay | [`docs/RESOURCE-OVERLAY.md`](docs/RESOURCE-OVERLAY.md) |
| Resource protocol v2 migration target | [`docs/RESOURCE-CONTRACT-V2.md`](docs/RESOURCE-CONTRACT-V2.md) |
| Authored graph | [`storage/local/`](storage/local/) |
| Neo4j expression | [`storage/neo4j/`](storage/neo4j/) |
| Storage declarations and contributor registry | [`k-graph.toml`](k-graph.toml) |

The repository is K's workspace. It owns the model and the means to validate,
project, and eventually query K. The authored Directory graph is its current
authoritative persistence; generated Neo4j Cypher is a derived persistence
expression. Changing the active persistence must not change this contract.

Translation must preserve node identity and semantics, the `g`, `l`, and `r`
edge families, and the accepted resource overlay.

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

## 5. Resource overlay

The registered contributor set is:

```text
research
studio
```

The accepted resource relation is:

$$
P_{\mathcal K}
\subseteq
\bigcup_{c\in C}(V\times\{c\}\times D_c\times F)
$$

Each tuple $(v,c,d,f)$ registers one logical resource for a K node,
contributor, contributor-owned domain, and format. Its durable identity is
`(node id, contributor, domain, format)`. Stores expose replicas and are not
part of that identity.

The Directory projection expresses the relation directly:

```yaml
contributors:
  research:
    documents:
      - md
  studio:
    scenes:
      - loci-project
    videos:
      - mp4
```

Nodes with no accepted resources use `contributors: {}`. Empty resource lists
do not encode proposal provenance.

Resource declarations do not change TLF kind or topology. Exact change-level
provenance belongs to a future accepted-proposal history. The canonical
resource model is in [`docs/RESOURCE-OVERLAY.md`](docs/RESOURCE-OVERLAY.md);
contributor responsibilities are in
[`docs/CONTRIBUTORS.md`](docs/CONTRIBUTORS.md).

## 6. Proposals

Registered contributors may asynchronously propose node or relationship
creation, replacement, patching, or deletion against a known graph revision.
The combined candidate graph is validated and accepted or rejected atomically.

The current workflow is manual. Its conceptual envelope and validation stages
are described in [`docs/PROPOSALS.md`](docs/PROPOSALS.md).

## 7. Representation contract

The repository manifest names the authoritative storage, the available
projections, and the allowed contributor domains and formats. It contains no
credentials, machine-specific paths, external repository locations, or
content URLs.

The Directory and Neo4j documents define how the same model is expressed:

- [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md)
- [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md)

Generated Neo4j Cypher is derived and is regenerated through the repository
tooling.

## 8. Versioned migration target

This version of the repository contract describes the active v1 graph files.
The accepted target for the next resource migration is
[`docs/RESOURCE-CONTRACT-V2.md`](docs/RESOURCE-CONTRACT-V2.md). It introduces
hierarchical resource addresses, explicit resource keys, versioned protocols,
and canonical SHA-256 digests without changing K's ownership of topology.

The v2 document does not authorize mixed serialization inside the active
graph. Directory nodes, Neo4j generation, contributor inventories, and
validators move together in the explicit migration phases.
