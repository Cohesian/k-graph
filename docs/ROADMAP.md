# Pending work

K's topology and resource protocol v2 are active in the Directory and Neo4j
projections. The Directory Projection remains the Git-versioned authority.

## 1. Unified K interface

Provide one read and proposal interface independent of persistence:

```text
caller → K interface → Directory | Neo4j
```

The interface should expose graph semantics—node selection, rooted paths,
ordered children, bounded Topic or Lecture views, relations, and accepted
resources—without leaking backend-specific commands.

## 2. Accepted-resource queries

For contributor $c$, K can expose:

$$
\pi_c(K)
=
\{(\operatorname{id}(v),\operatorname{path}(v),H,p,q,z)\}.
$$

This communicates accepted identity and integrity, not contributor storage.
Tether can join that projection with a contributor inventory to report exact
matches, missing resources, unregistered resources, and mismatched protocols
or digests.

## 3. Proposal pipeline

Turn the manual proposal envelope into an atomic workflow:

```text
prepare → submit → validate → review → accept | reject
```

Validation should cover the complete candidate graph and protocol-derived
resource digests. Accepted history may later record proposal authorship,
licensing decisions, and path changes.

## 4. Persistence

Load and verify generated Cypher in local Neo4j and Aura when useful. The same
K interface should operate either persistence. Backup and remote credentials
belong to infrastructure configuration, not the graph contract.

## 5. Consumer snapshots

Consumers may join a selected K revision with contributor inventories and
materialize their own resolved view:

```text
K revision + accepted contributor resources
→ select exact replicas or publications
→ resolve or fetch
→ build consumer-local snapshot
```

Such snapshots are derived and non-authoritative. Consumers decide layout and
composition; K does not encode Website- or renderer-specific structure.

## 6. Reindexing

A grouping change may alter a path and every descendant path. K should expose:

```text
(id, old_path, new_path)
```

Contributor resources remain durably joined by UUID. Path-mirroring stores may
consume the change set without treating topology movement as content change.

## 7. Independent terminology migration

Renaming TLF's leaf kind from File to Entry is independent of resource
protocol v2. If adopted, TLF-to-TLE must update topology terminology,
representations, tooling, and consumers atomically; resource keys and
protocols remain unchanged.
