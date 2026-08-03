# Neo4j representation

This directory contains the Neo4j-language expression of the k-graph.

- [`schema.cypher`](schema.cypher) declares constraints and indexes.
- [`k-graph.cypher`](k-graph.cypher) is the generated complete graph.

Generate the graph from the repository root:

```bash
.venv/bin/kgraph-to-neo4j --out storage/neo4j/k-graph.cypher
```

Load it into a running local Neo4j database:

```bash
cypher-shell \
  -a bolt://localhost:7687 \
  -u neo4j \
  -d neo4j \
  -f storage/neo4j/schema.cypher

cypher-shell \
  -a bolt://localhost:7687 \
  -u neo4j \
  -d neo4j \
  -f storage/neo4j/k-graph.cypher
```

`cypher-shell` prompts for the password. The same generated graph can target a
local instance or Aura by changing the connection address and credentials.
