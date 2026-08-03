# Pending work

The graph model and its Directory and Neo4j representations are established.
Research now has a local contributor-owned storage resolver using the selector
model below. K's unified query interface, a shared contributor protocol, and
the Studio resolver remain pending while the graph is mirrored manually.

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
(\operatorname{id}(v),\operatorname{path}(v),\phi(c,v))
\mid
(c,v)\in E_c
\right\}
$$

This projection communicates accepted identities, current paths, and declared
content forms. It does not communicate storage infrastructure.

## 3. Contributor discovery and resolution

Each contributor owns a small interface over its storage. Two operations are
needed.

Discovery reports what is currently available for a selector:

$$
A_c:
\operatorname{Selector}
\longrightarrow
\mathcal P(\operatorname{Format}\times\operatorname{Source}\times\operatorname{State})
$$

Resolution returns locations matching a requested selector, format, and optional
source:

$$
R_c:
\operatorname{Selector}\times\operatorname{Format}\times\operatorname{Source}?
\rightharpoonup
\mathcal P(\operatorname{Location})
$$

The result is a set because the same logical content may have several replicas.
The mapping is partial because content may be unavailable or inaccessible.

Conceptually:

```text
research content list --id <id>
research content resolve --path <path> --format md --source drive

studio content list --path <path>
studio content resolve --id <id> --format mp4 --source youtube
```

Each resolved location should minimally identify:

```text
id
path
format
source
uri
```

Useful optional fields are availability state, media type, version, checksum,
and access class. Credentials and tokens remain inside the contributor's own
storage boundary.

Initial source plans are:

| Contributor | Sources |
|---|---|
| Research | local directory, Google Drive |
| Studio | local directory, Google Drive, YouTube |

## 4. Content identity

Before fixing the contributor CLI contract, decide whether this tuple names one
logical content object:

```text
(K id, contributor, format)
```

If a node may have several Markdown papers, videos, languages, or editions in
the same format, the contract will also need a contributor-owned `content_ref`
or `variant`. This decision should precede automation.

## 5. Website snapshot

The eventual Website content build can remain offline and reproducible:

```text
query accepted K snapshot
→ discover contributor content
→ resolve selected replicas
→ fetch content
→ build static Website snapshot
```

Versions or checksums in resolver responses would let a Website build record
exactly which content snapshot it consumed.

## Suggested order

1. Continue manually maintaining the Directory and Neo4j mirrors.
2. Extend the established Research local storage to Drive, and establish
   Studio storage independently.
3. Decide content multiplicity.
4. Specify the K query interface.
5. Specify the shared contributor discovery/resolution protocol.
6. Implement the Research and Studio adapters separately.
7. Connect the Website snapshot pipeline after the interfaces have real data.

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
