# Neo4j projection

## 1. Meaning

The Neo4j Projection expresses the TLF k-graph as a labeled property graph.

It is one concrete representation of the mathematical object defined in
[`TLF.md`](TLF.md). Nodes become Neo4j nodes, edge families become explicit
relationships, and local descriptions become properties.

## 2. Nodes

Every node carries the common `KNode` label and one kind label:

```text
(:KNode:Topic)
(:KNode:Lecture)
(:KNode:File)
(:KNode:File:Draft)
```

The kind correspondence is:

| TLF kind | Neo4j labels |
|---|---|
| `T` | `KNode`, `Topic` |
| `L` | `KNode`, `Lecture` |
| `F` | `KNode`, `File` |
| `Fd` | `KNode`, `File`, `Draft` |

## 3. Node properties

Initial properties are:

| Property | Meaning |
|---|---|
| `key` | Unique root-derived graph path; `K` for the root |
| `local_id` | Final local path component |
| `kind` | Exact `T`, `L`, `F`, or `Fd` |
| `title` | Human-facing title |
| `description` | Local description |
| `research` | Declared research representations |
| `media_scenes` | Declared scene representations |
| `media_videos` | Declared video representations |

Example:

```cypher
(:KNode:File {
  key: 'T-computer-science/L-composite/F-04-TLF-composite',
  local_id: 'F-04-TLF-composite',
  kind: 'F',
  title: 'TLF Composite',
  description: 'Topic / Lecture / File composite pattern for a knowledge corpus.',
  research: ['md'],
  media_scenes: ['py'],
  media_videos: ['mp4', 'youtube']
})
```

Neo4j properties cannot contain arbitrary nested maps. The abstract content
tree is therefore represented by named list properties.

The portable identity is `key`, not Neo4j's internal element id.

## 4. Grouping relationships

The `g` axis is:

```cypher
(parent:KNode)-[:GROUPS {position: 0}]->(child:KNode)
```

`position` is a zero-based authored sibling position.

The grouping laws are:

- only Topic and Lecture nodes have outgoing `GROUPS`;
- `K` has no incoming `GROUPS`;
- every other node has exactly one incoming `GROUPS`;
- sibling positions are unique non-negative integers;
- every node is reachable from `K`; and
- grouping is acyclic.

Thus the grouping projection is a rooted ordered tree and therefore a DAG.

## 5. Linear relationships

The `l` axis uses one physical direction:

```cypher
(previous:KNode)-[:NEXT]->(next:KNode)
```

The relationship is `next` when traversed forward and `prev` when traversed
backward.

The linear laws are:

- every node has at most one incoming `NEXT`;
- every node has at most one outgoing `NEXT`;
- all TLF kinds may participate;
- the initial profile rejects linear cycles; and
- `NEXT` never changes structural layout.

No separate physical `PREV` relationship is required.

## 6. Related relationships

The `r` axis is:

```cypher
(origin:KNode)-[:RELATED_TO]->(target:KNode)
```

or, when scored:

```cypher
(origin:KNode)-[:RELATED_TO {weight: 0.72}]->(target:KNode)
```

The related laws are:

- all TLF kinds may participate;
- weight is optional;
- direction is preserved;
- fan-out and cycles are allowed; and
- related relationships never change structural layout.

Until a weight scale is standardized, a numeric value is preserved without
assuming universal semantics.

## 7. Schema

The portable key is unique:

```cypher
CREATE CONSTRAINT k_node_key IF NOT EXISTS
FOR (n:KNode)
REQUIRE n.key IS UNIQUE;
```

Kind queries are indexed:

```cypher
CREATE INDEX k_node_kind IF NOT EXISTS
FOR (n:KNode)
ON (n.kind);
```

Degree, acyclicity, reachability, and sibling-position rules require graph
validation in addition to database constraints.

## 8. Local knowledge

For a Neo4j node $v$, local knowledge is:

$$
\operatorname{loc}(v)
=
\left(
\operatorname{properties}(v),
E_g^-(v),E_g^+(v),
E_l^-(v),E_l^+(v),
E_r^-(v),E_r^+(v)
\right)
$$

The graph engine stores the node and its incident relationships directly.
Global paths, forests, chains, backlinks, and neighborhoods emerge from
traversal.

## 9. Basic queries

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

### Grouping projection

```cypher
MATCH (parent:KNode)-[g:GROUPS]->(child:KNode)
RETURN parent, g, child;
```

### Topic nodes

```cypher
MATCH (topic:KNode:Topic)
RETURN topic
ORDER BY topic.key;
```

### Lecture nodes

```cypher
MATCH (lecture:KNode:Lecture)
RETURN lecture
ORDER BY lecture.key;
```

## 10. Representation summary

| TLF concept | Neo4j expression |
|---|---|
| Corpus node | `(:KNode)` |
| Topic | `(:KNode:Topic)` |
| Lecture | `(:KNode:Lecture)` |
| File | `(:KNode:File)` |
| Draft File | `(:KNode:File:Draft)` |
| Node metadata | Properties |
| Grouping | `[:GROUPS {position}]` |
| Linear | `[:NEXT]` |
| Related | `[:RELATED_TO {weight?}]` |
| Portable identity | `key` |
| Local adjacency | Incident relationships |
