# Pending work

The graph model and its Directory and Neo4j representations are established.
K now stores domain-aware resources, and the shared Tether bridge is validated
against both Research and Studio. The Directory Projection remains the current
Git-versioned authority. Website migration can consume that representation
directly while a unified K interface and remote persistence remain pending.

## Established identity

Every current node now materializes a UUIDv4 `id`. The Directory tree and
Neo4j `GROUPS` relationships each derive the rooted address; Neo4j does not
persist it as a node property.

```text
id        stable identity
path      current address derived from the g projection
local_id  local readable name
```

`path` is unique within one accepted graph revision. `id` is immutable across
moves and revisions.

The future selector contract is:

```text
selector := id | path | (id, path)
```

When both values are supplied, they must identify the same node. Contributors
may index storage by either selector, but `id` is the durable choice and `path`
is the readable lookup address.

## 1. Unified K query interface

Define one read interface independent of graph persistence, with adapters for:

- the Directory Projection; and
- Neo4j, whether local or Aura.

The eventual CLI should expose graph meaning rather than backend-specific
commands—for example node lookup, root paths, ordered children, contributor
relations, and bounded Topic or Lecture views.

```text
caller → K query interface → Directory | Neo4j
```

Directory remains authoritative for now. Cypher generation and loading into
local Neo4j or Aura remain manual.

## 2. Contributor projection

For each contributor $c$, K can expose the portion of its accepted registry
relevant to that contributor:

$$
\pi_c(K)
=
\left\{
(\operatorname{id}(v),\operatorname{path}(v),d,f)
\;\middle|\;
(v,c,d,f)\in P_K
\right\}
$$

This projection communicates accepted identities, current paths, and declared
content forms. It does not communicate storage infrastructure.

## 3. Contributor discovery and resolution

Each contributor owns one localized protocol document. It declares:

$$
B_c\subseteq D_c\times S_c\times F
$$

where domains $D_c$ and stores $S_c$ remain independent axes and $B_c$ binds
the formats made available between them. Route inventories materialize target
availability.

Discovery reports what is currently available for a selector:

$$
A_c:
\operatorname{Selector}
\longrightarrow
\mathcal P(\operatorname{Format}\times\operatorname{Store}\times\operatorname{State})
$$

Resolution returns locations matching a requested selector, contributor
domain, format, and optional store:

$$
R:
\operatorname{Selector}\times C\times D\times\operatorname{Format}
\times\operatorname{Store}?
\rightharpoonup
\mathcal P(\operatorname{Location})
$$

The result is a set because the same logical content may have several replicas.
The mapping is partial because content may be unavailable or inaccessible.

Tether evaluates the contributor protocol directly:

```text
tether resource list <contributor> --id <id>
tether resource resolve <contributor> --path <path> --format md
```

Each resolved location should minimally identify:

```text
id
path
format
store
uri
```

Useful optional fields are availability state, media type, version, checksum,
and access class. Credentials and tokens remain inside the contributor's own
storage boundary.

Initial store plans are:

| Contributor | Stores |
|---|---|
| Research | local directory, Google Drive |
| Studio | local directory, Google Drive, YouTube |

## 4. Content identity

Protocol version 1 settles one logical resource as:

```text
(K id, contributor, domain, format)
```

There is no resource name or variant. Repeated physical locations are replicas
of the same logical resource. If a future use case genuinely needs several
same-format resources under one node, contributor, and domain, it requires a
versioned identity extension rather than an implicit filename distinction.

## 5. Website snapshot

The initial Website content build can remain offline and reproducible without
waiting for the unified K query interface:

```text
acquire the Git-versioned Directory Projection
→ discover contributor content
→ resolve selected replicas
→ fetch content
→ create a consumer-local resolved projection
→ build static Website snapshot
```

The resolved projection is generated and ignored by Git. It preserves each
`(contributor, domain, format)` declaration and adds the selected store and
URI; it never mutates authoritative K. Git commit ids can identify the current
internal inputs. Per-resource digests remain a later integrity extension.

## Suggested order

1. Stabilize the Directory authority and deterministically generated Neo4j
   expression.
2. Stabilize the Research and Studio contributor inventories through Tether.
3. Migrate the Website build from legacy Foundations inputs to a local K and
   contributor snapshot.
4. Load and verify K in local Neo4j, then Aura when useful.
5. Add the backend-agnostic K interface when more than one persistence must be
   operated regularly.
6. Add approved remote contributor maps and content digests when those stores
   enter the publication flow.

## Reindexing

A change to the grouping projection may change one path and every descendant
path below it. K should eventually publish the accepted path changes as:

```text
(id, old_path, new_path)
```

Contributor content indexed by `id` remains reachable without moving its
storage. Contributors that mirror paths can consume the change set and update
their local indexes. This avoids treating a topology rearrangement as a change
of content identity.
