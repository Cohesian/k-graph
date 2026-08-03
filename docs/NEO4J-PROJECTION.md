# Neo4j projection

## 1. Meaning

The Neo4j Projection expresses the same TLF object as a labeled property graph.
Knowledge nodes and contributors become Neo4j nodes; topology and attribution
become explicit relationships.

## 2. Knowledge nodes

Every knowledge node has the common `KNode` label and a kind label:

| TLF kind | Neo4j labels |
|---|---|
| `T` | `KNode`, `Topic` |
| `L` | `KNode`, `Lecture` |
| `F` | `KNode`, `File` |
| `Fd` | `KNode`, `File`, `Draft` |

Its intrinsic and identity properties are:

| Property | Meaning |
|---|---|
| `key` | Portable root-derived grouping path; `K` for the root |
| `local_id` | Final local path component |
| `kind` | Exact `T`, `L`, `F`, or `Fd` value |
| `title` | Human-facing title |
| `description` | Concise local meaning |

```cypher
(:KNode:File {
  key: 'T-computer-science/L-composite/F-04-TLF-composite',
  local_id: 'F-04-TLF-composite',
  kind: 'F',
  title: 'TLF Composite',
  description: 'Topic / Lecture / File composite pattern for a knowledge corpus.'
})
```

## 3. Topology

### Grouping

```cypher
(parent:KNode)-[:GROUPS {position: 0}]->(child:KNode)
```

`position` is the zero-based authored sibling position. `K` has no grouping
parent; every other node has exactly one. Only Topic and Lecture nodes may
group children, and the full projection is rooted and acyclic.

### Linear

```cypher
(previous:KNode)-[:NEXT]->(next:KNode)
```

Every node has at most one incoming and one outgoing `NEXT`. Incoming traversal
is `prev`; outgoing traversal is `next`. No separate `PREV` relationship is
stored.

### Related

```cypher
(origin:KNode)-[:RELATED_TO {weight: 0.72}]->(target:KNode)
```

The optional weight is preserved without imposing a universal scale.
Direction matters; fan-out and cycles are allowed.

## 4. Contributor overlay

Each registered contributor is a node:

```cypher
(:Contributor {id: 'research'})
```

Its participation in a knowledge node is explicit:

```cypher
(:Contributor {id: 'research'})
  -[:CONTRIBUTED {formats: ['md']}]->
(:KNode {key: $key})
```

An empty `formats` list records contribution without attached content. These
relationships are attribution, not TLF topology.

## 5. Schema

```cypher
CREATE CONSTRAINT k_node_key IF NOT EXISTS
FOR (n:KNode)
REQUIRE n.key IS UNIQUE;

CREATE CONSTRAINT contributor_id IF NOT EXISTS
FOR (c:Contributor)
REQUIRE c.id IS UNIQUE;

CREATE INDEX k_node_kind IF NOT EXISTS
FOR (n:KNode)
ON (n.kind);
```

Degree, reachability, acyclicity, and sibling-position rules are checked by the
projection tooling.

## 6. Local knowledge

For a knowledge node $v$:

$$
\operatorname{loc}(v)=
\left(
\nu(v),
E_g^-(v),E_g^+(v),
E_l^-(v),E_l^+(v),
E_r^-(v),E_r^+(v),
E_c^-(v)
\right)
$$

where $\nu(v)$ is `kind`, `title`, and `description`, while $E_c^-(v)$ is its
incoming contributor attribution. Paths, forests, chains, and neighborhoods
emerge through traversal.

## 7. Basic queries

### Select a node

```cypher
MATCH (n:KNode {key: $key})
RETURN n;
```

### Root-to-node path

```cypher
MATCH p = (:KNode {key: 'K'})-[:GROUPS*]->(n:KNode {key: $key})
RETURN [x IN nodes(p) | x.local_id] AS local_path;
```

### Ordered children

```cypher
MATCH (parent:KNode {key: $key})-[g:GROUPS]->(child:KNode)
RETURN child, g.position
ORDER BY g.position;
```

### Previous and next

```cypher
MATCH (n:KNode {key: $key})
OPTIONAL MATCH (prev:KNode)-[:NEXT]->(n)
OPTIONAL MATCH (n)-[:NEXT]->(next:KNode)
RETURN prev, n, next;
```

### Related neighborhood

```cypher
MATCH (n:KNode {key: $key})-[r:RELATED_TO]-(other:KNode)
RETURN other, r.weight, startNode(r).key = n.key AS outgoing;
```

### Contributors and formats

```cypher
MATCH (c:Contributor)-[a:CONTRIBUTED]->(n:KNode {key: $key})
RETURN c.id AS contributor, a.formats AS formats
ORDER BY contributor;
```

## 8. Representation summary

| TLF concept | Neo4j expression |
|---|---|
| Corpus node | `(:KNode)` |
| Intrinsic semantics | `kind`, `title`, `description` properties |
| Grouping | `[:GROUPS {position}]` |
| Linear | `[:NEXT]` |
| Related | `[:RELATED_TO {weight?}]` |
| Contributor | `(:Contributor)` |
| Attribution | `[:CONTRIBUTED {formats}]` |
| Portable identity | `KNode.key` |
