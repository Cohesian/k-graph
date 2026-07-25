# k-graph tools

## `to_neo4j.py`

Reads the complete local Directory Projection and writes the equivalent graph
as Cypher.

Validate without writing:

```bash
python tools/to_neo4j.py
```

Generate the Neo4j expression:

```bash
python tools/to_neo4j.py --out cypher/k-graph.cypher
```

The translator:

- discovers every composite and leaf;
- derives graph keys from directory paths;
- preserves `edges.g` order as `GROUPS.position`;
- collapses reciprocal `prev`/`next` declarations into one `NEXT`;
- expresses `edges.r` as `RELATED_TO`;
- preserves document, notebook, scene, video, and YouTube declarations;
- validates grouping coverage, reachability, linear reciprocity, and degrees;
- never connects to Neo4j; and
- never changes the Directory Projection.

The generated Cypher is derived. Regenerate it rather than editing it.

## `validate_kgraph.py`

Validates the Directory Projection and its configured data locations:

```bash
python tools/validate_kgraph.py
```

## `resolve_kgraph.py`

Resolves a graph key and abstract data tree through `k-graph.toml`:

```bash
python tools/resolve_kgraph.py \
  media.videos \
  T-computer-science/L-composite/F-04-TLF-composite
```
