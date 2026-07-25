# Cypher

This directory contains the Neo4j-language expression of the k-graph.

## Schema

[`schema.cypher`](schema.cypher) defines the idempotent key constraint and kind
index.

## Complete graph

Generate [`k-graph.cypher`](k-graph.cypher) from the Directory Projection:

```bash
python tools/to_neo4j.py --out cypher/k-graph.cypher
```

Load it into a running local Neo4j database:

```bash
cypher-shell \
  -a bolt://localhost:7687 \
  -u neo4j \
  -d neo4j \
  -f cypher/k-graph.cypher
```

`cypher-shell` prompts for the password. Do not put credentials in commands,
configuration, or generated files.

Cypher is the first translation target because this graph is small and the
same artifact can be executed against local Neo4j or Aura. The offline
`neo4j-admin database import full` CSV workflow is available later if graph
scale justifies it.
