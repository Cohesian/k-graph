# Neo4j projection

## 1. Meaning

The Neo4j Projection stores the TLE object as a labeled property graph.
Knowledge nodes and contributors become Neo4j nodes; topology and accepted
resources become explicit relationships.

## 2. Knowledge nodes

Every knowledge node has the common `KNode` label and a kind label:

| TLE kind | Neo4j labels |
|---|---|
| `T` | `KNode`, `Topic` |
| `L` | `KNode`, `Lecture` |
| `E` | `KNode`, `Entry` |
| `Ed` | `KNode`, `Entry`, `Draft` |

Its identity and semantic properties are:

| Property | Meaning |
|---|---|
| `id` | Immutable UUID identity |
| `local_id` | Local readable name used to form a rooted path |
| `kind` | Exact `T`, `L`, `E`, or `Ed` value |
| `title` | Human-facing title |
| `description` | Concise local meaning |

```cypher
(:KNode:Entry {
  id: '42292902-3874-4d54-87ec-0e1b7362af13',
  local_id: 'E-04-TLE-composite',
  kind: 'E',
  title: 'TLE Composite',
  description: 'Topic / Lecture / Entry composite pattern for a knowledge corpus.'
})
```

Neo4j merges and connects knowledge nodes by `id`. It does not persist a
rooted `path` property: the unique path is derived from `GROUPS` topology and
the `local_id` values encountered from `K`. Regrouping therefore changes the
route without requiring duplicated node metadata to be synchronized.

## 3. Topology

Grouping:

```cypher
(parent:KNode)-[:GROUPS {position: 0}]->(child:KNode)
```

Linear traversal:

```cypher
(previous:KNode)-[:NEXT]->(next:KNode)
```

Related knowledge:

```cypher
(origin:KNode)-[:RELATED_TO {weight: 0.72}]->(target:KNode)
```

`GROUPS.position` preserves authored sibling order. Every node has at most one
incoming and one outgoing `NEXT`. Related edges preserve direction, may fan
out or cycle, and may carry an optional weight.

## 4. Resource overlay

```cypher
(:Contributor {id: 'research'})
  -[:PROVIDES {
    hierarchy: ['documents'],
    key: 'md',
    protocol: 'markdown-file@1',
    sha256: 'aaacecaa42528397cc3cca3c88141863d7f381a50bec28bdacf6492dc1472386'
  }]->
(:KNode {id: $id})
```

One `PROVIDES` relationship represents one accepted resource at
`(K node id, contributor, hierarchy, key)`. Its protocol defines the resource
boundary and digest procedure; `sha256` fixes the accepted bytes. Resource
relationships are not TLE topology, and physical stores remain outside Neo4j.

## 5. Schema

```cypher
CREATE CONSTRAINT k_node_id IF NOT EXISTS
FOR (n:KNode)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT contributor_id IF NOT EXISTS
FOR (c:Contributor)
REQUIRE c.id IS UNIQUE;

CREATE INDEX k_node_kind IF NOT EXISTS
FOR (n:KNode)
ON (n.kind);
```

Rooted-path uniqueness follows from the validated grouping laws rather than a
duplicated property constraint. Degree, reachability, acyclicity, and sibling
positions are checked by the projection tooling.

## 6. Selector queries

UUID lookup is direct:

```cypher
MATCH (n:KNode {id: $id})
RETURN n;
```

To derive that node's current rooted path:

```cypher
MATCH p = (:KNode {local_id: 'K'})-[:GROUPS*0..]->(n:KNode {id: $id})
WITH n, nodes(p) AS lineage
RETURN n,
  CASE
    WHEN size(lineage) = 1 THEN 'K'
    ELSE reduce(
      path = '',
      x IN tail(lineage) |
      path + CASE WHEN path = '' THEN '' ELSE '/' END + x.local_id
    )
  END AS path;
```

Lookup by rooted path computes the address from topology and then compares it:

```cypher
MATCH p = (:KNode {local_id: 'K'})-[:GROUPS*0..]->(n:KNode)
WITH n, nodes(p) AS lineage
WITH n,
  CASE
    WHEN size(lineage) = 1 THEN 'K'
    ELSE reduce(
      path = '',
      x IN tail(lineage) |
      path + CASE WHEN path = '' THEN '' ELSE '/' END + x.local_id
    )
  END AS derived_path
WHERE derived_path = $path
  AND ($id IS NULL OR n.id = $id)
RETURN n, derived_path AS path;
```

Passing `$id` in the second query requires both selectors to identify the same
node. Path lookup performs traversal; a future query layer may cache derived
addresses without making the cache authoritative.

Ordered children:

```cypher
MATCH (parent:KNode {id: $id})-[g:GROUPS]->(child:KNode)
RETURN child, g.position
ORDER BY g.position;
```

Previous and next:

```cypher
MATCH (n:KNode {id: $id})
OPTIONAL MATCH (prev:KNode)-[:NEXT]->(n)
OPTIONAL MATCH (n)-[:NEXT]->(next:KNode)
RETURN prev, n, next;
```

Related neighborhood:

```cypher
MATCH (n:KNode {id: $id})-[r:RELATED_TO]-(other:KNode)
RETURN other, r.weight, startNode(r).id = n.id AS outgoing;
```

Resources by contributor, hierarchy, and key:

```cypher
MATCH (c:Contributor)-[r:PROVIDES]->(n:KNode {id: $id})
RETURN c.id AS contributor,
       r.hierarchy AS hierarchy,
       r.key AS resource_key,
       r.protocol AS protocol,
       r.sha256 AS sha256
ORDER BY contributor, hierarchy, resource_key;
```

## 7. Representation summary

| TLE concept | Neo4j expression |
|---|---|
| Knowledge node | `(:KNode)` |
| Stable identity | `KNode.id` |
| Rooted address | derived from `GROUPS` and `local_id` |
| Intrinsic semantics | `kind`, `title`, `description` properties |
| Grouping | `[:GROUPS {position}]` |
| Linear | `[:NEXT]` |
| Related | `[:RELATED_TO {weight?}]` |
| Contributor | `(:Contributor)` |
| Resource overlay | `[:PROVIDES {hierarchy, key, protocol, sha256}]` |
