# k-graph contract

Version: **0.7.0**

Status: **active**

## 1. Purpose

The k-graph is Cohesian's accepted knowledge registry. It provides stable
knowledge-node identity, intrinsic node semantics, explicit topology, and
accepted contributor resources without embedding contributed content bodies.

The distinguished root is `K`, a Topic.

## 2. Authorities

| Concern | Authority |
|---|---|
| Mathematical model | [`docs/TLF.md`](docs/TLF.md) |
| Accepted resource model | [`docs/RESOURCE-CONTRACT-V2.md`](docs/RESOURCE-CONTRACT-V2.md) |
| Authored graph | [`storage/local/`](storage/local/) |
| Neo4j expression | [`storage/neo4j/`](storage/neo4j/) |
| Persistence and contributor registry | [`k-graph.toml`](k-graph.toml) |

The repository is K's workspace. The authored Directory graph is its current
authority; generated Neo4j Cypher is a derived expression. Translation must
preserve node identity, semantics, the `g`, `l`, and `r` edge families, and
every accepted resource record.

## 3. Node semantics and identity

Every node has:

```yaml
id: 499ff1af-eed7-425d-9fed-e357ec2e0b97
kind: T | L | F | Fd
title: Human-facing title
description: Concise local description
```

Kinds are Topic composite (`T`), Lecture composite (`L`), File leaf (`F`),
and draft File leaf (`Fd`). `kind` remains semantic even when a representation
can derive it.

A node has two selectors:

| Selector | Meaning |
|---|---|
| `id` | Immutable UUID, stable across moves and revisions |
| `path` | Address derived from the current grouping projection |

When both are supplied, they must resolve to the same node. Neo4j stores the
UUID and derives the rooted path through `GROUPS`; internal Neo4j element ids
are never portable identity.

## 4. Topology

| Axis | Neo4j expression | Meaning |
|---|---|---|
| `g` | `GROUPS {position}` | Structural grouping and authored order |
| `l` | `NEXT` | Linear traversal; reverse traversal is `prev` |
| `r` | `RELATED_TO {weight?}` | Directed, optionally weighted relation |

The `g` projection is a rooted ordered tree and therefore a DAG. Every
non-root node has exactly one grouping parent; only `T` and `L` group children.
Each node has at most one incoming and one outgoing `NEXT`, and the linear
projection is acyclic. `RELATED_TO` may fan out and form cycles.

## 5. Accepted resources

For a K node $v$, registered contributor $c$, non-empty hierarchy $H$, and
resource key $p$, the durable address is:

$$
\bar a=(\operatorname{id}(v),c,H,p).
$$

K accepts exactly one record at that address:

$$
K(\bar a)=(q,z),
$$

where $q$ is a versioned protocol and $z$ is its canonical lowercase SHA-256.
The Directory expression is:

```yaml
contributions:
  c_research:
    h_documents:
      r_md:
        protocol: markdown-file@1
        sha256: aaacecaa42528397cc3cca3c88141863d7f381a50bec28bdacf6492dc1472386
```

The `c_`, `h_`, and `r_` prefixes mark contributor, hierarchy segment, and
resource key. Hierarchies may have arbitrary depth. A hierarchy may contain
both nested `h_` entries and local `r_` entries. Nodes without resources use
`contributions: {}`.

K stores neither content bytes nor physical locations. Contributors own those
and expose them through Tether-compatible inventories. Tether interprets the
protocol, computes digests, validates exact replicas, and resolves locations.
A hosted transformation is a publication, not an exact byte replica.

The active contract is fully specified in
[`docs/RESOURCE-CONTRACT-V2.md`](docs/RESOURCE-CONTRACT-V2.md).

## 6. Proposals

Registered contributors may asynchronously propose node, relationship, or
resource changes against a known graph revision. K evaluates the complete
candidate graph and accepts or rejects it atomically. The current workflow is
manual and is described in [`docs/PROPOSALS.md`](docs/PROPOSALS.md).

## 7. Representation contract

`k-graph.toml` names persistence paths and the registered contributor set. It
contains no credentials, machine-specific roots, contributor locations, or
content URLs.

The Directory and Neo4j projections describe the same graph:

- [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md)
- [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md)

Generated Cypher is always regenerated through the repository tooling.

## 8. Version boundary

Protocol v2 replaced the v1 `(node id, contributor, domain, format)` identity
with `(node id, contributor, hierarchy, resource key)` and added protocol-bound
digests. The active graph is entirely v2; mixed v1/v2 node serialization is
invalid. A later TLF-to-TLE terminology change is an independent topology
migration.
