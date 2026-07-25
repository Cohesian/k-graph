# k-graph contract

Version: **0.1.0**

Status: **initial rollout contract**

## 1. Purpose

The k-graph is Cohesian's knowledge index. It provides stable knowledge-node
identity, explicit graph topology, and abstract links to research and media
without embedding those content bodies.

The root is `K`, represented as a distinguished Topic.

The complete mathematical model is [`docs/TLF.md`](docs/TLF.md). This document
is the short normative storage and repository contract.

## 2. Authorities

The model separates its abstract definition from concrete expressions:

| Concern | Location |
|---|---|
| Mathematical TLF model | `docs/TLF.md` |
| Complete Directory Projection | `k-graph/` |
| Neo4j property-graph expression | `docs/NEO4J-PROJECTION.md` |
| Path and URI resolution | `k-graph.toml` |

Translation tooling must preserve node identity, properties, relationship
semantics, direction, and relationship properties between expressions.

## 3. Node contract

### Identity

A node's `local_id` is derived from its YAML filename or composite directory.
The YAML does not repeat the id.

The root's id is `K`. Other ids retain the established TLF prefixes.

### Kinds

| Kind | Meaning |
|---|---|
| `T` | Topic composite |
| `L` | Lecture composite |
| `F` | File leaf |
| `Fd` | Draft File leaf |

`Fd` remains a flat kind with the same graph capabilities as `F`. A database
projection may additionally expose `draft: true` or a `Draft` label.

### Conceptual node data

Every node has:

```yaml
kind: T | L | F | Fd
title: Human-facing title
description: Concise local description
data: {}
```

The current Directory Projection declares:

| Data branch | Values | Meaning |
|---|---|---|
| `documents` | `md`, `ipynb` | Research document or notebook |
| `media.scripts.scenes` | `py` | Python scene implementation |
| `media.videos` | `mp4` | Rendered file; published YouTube presence comes from the provider map |

Lists contain unique values. An empty list means that representation is not
declared for the node.

In the Directory Projection, `edges` is a top-level sibling of `data`:

```yaml
edges:
  g: []
  l:
    prev: null
    next: null
  r: []
```

Node `data` must not contain:

- graph relationships;
- paths derived from graph position;
- provider URLs or ids;
- database labels, coordinates, or internal ids; or
- document, scene, or video bodies.

## 4. Graph contract

Every materialized node carries the common `KNode` label and one kind
projection:

```text
(:KNode:Topic)
(:KNode:Lecture)
(:KNode:File)
(:KNode:File:Draft)
```

Its unique portable `key` is the root-derived `g_path`. Moving or renaming a
node is an explicit key migration. Neo4j internal element ids are never
portable identity.

### `g`: grouping

```text
(parent)-[:GROUPS {position: integer}]->(child)
```

- `K` has no grouping parent.
- Every other node has exactly one grouping parent.
- The projection is acyclic.
- Zero-based sibling `position` values are unique and define authored order.
- Only `GROUPS` affects structural layout and canonical graph paths.

The initial grouping projection is therefore a rooted, ordered arborescence and
also a DAG.

### `l`: linear traversal

```text
(previous)-[:NEXT]->(next)
```

- A node has at most one outgoing `NEXT`.
- A node has at most one incoming `NEXT`.
- Outgoing traversal is `next`; incoming traversal is `prev`.
- Linear relationships may connect any node kind.
- Linear components are acyclic in contract 0.1.0.
- Linear relationships do not affect structural layout.

One stored relationship represents both local traversal perspectives. A second
physical `PREV` relationship would duplicate the same fact.

### `r`: related knowledge

```text
(origin)-[:RELATED_TO {weight: number?}]->(target)
```

- Related relationships may connect any node kind.
- Cycles are allowed.
- `weight` is optional.
- An absent weight means related but unscored.
- Direction is preserved; consumers must not assume symmetry.
- Related relationships do not affect structural layout.

The semantic scale for weights can be tightened by a later version without
moving the relationship out of Neo4j.

## 5. Derived values

These values emerge from the complete graph:

| Value | Derivation |
|---|---|
| `local_id` | Node YAML filename or composite directory |
| `g_path` / `key` | Ordered `GROUPS` traversal from `K` |
| `group_index` | Ordered grouping positions |
| `x`, `y` | Layout of a selected grouping projection |
| `prev`, `next` | Incoming and outgoing `NEXT` |
| related neighborhood | `RELATED_TO` traversal |

`g_path` is the canonical content key. Display indexes and coordinates are not
identity.

## 6. Resolution contract

`k-graph.toml` maps an abstract declaration to a path or URI:

```text
(g_path, data branch, representation, source?)
    -> resolve with k-graph.toml
    -> filesystem path or final URI
```

The configuration declares:

- valid data branches and representations;
- available sources;
- default source selection;
- roots and URI patterns; and
- explicit provider-id maps where derivation is insufficient.

Research Markdown resolves to Foundations. Python scenes resolve to Studio.
MP4 may resolve locally or through Drive. YouTube resolves through an explicit
published-video mapping.

## 7. Repository boundaries

| Repository/system | Owns |
|---|---|
| `Cohesian/k-graph` | TLF theory, Directory and Neo4j expressions, resolver config, validation, and translation tooling |
| Neo4j local/Aura | Live `g`, `l`, and `r` relationships |
| `Cohesian/foundations` | Markdown research documents and research workspace |
| `Cohesian/studio` | Scene code and video-production workflow |
| `Cohesian/site` | Public graph and content projections |
| `Cohesian/Organization` | Cross-repository governance and rollout |
| `Cohesian/core` | Constitutional principles and identity |

## 8. Representation documents

- [`docs/TLF.md`](docs/TLF.md) defines the representation-independent
  mathematics.
- [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) defines the
  Git-friendly complete graph expression.
- [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) defines labels,
  properties, relationships, constraints, and queries.

## 9. T1 boundary

T1 establishes this repository, the mathematical and representation contracts,
the copied Directory Projection and resolver configuration, and a translator
that emits Neo4j-readable Cypher.

Research and media bodies remain in their owning repositories and systems.
