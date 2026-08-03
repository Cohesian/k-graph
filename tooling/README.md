# k-graph tooling

This directory is a small Python project for validating the authoritative
Directory Projection and generating its Neo4j expression.

## Install

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ./tooling
```

## Validate

```bash
.venv/bin/kgraph-validate
```

Validation covers intrinsic fields, contributor ids and formats, grouping
coverage and reachability, linear reciprocity and degree, and related targets.

## Generate Neo4j Cypher

```bash
.venv/bin/kgraph-to-neo4j --out representations/neo4j/k-graph.cypher
```

The command emits `KNode`, `Contributor`, `GROUPS`, `NEXT`, `RELATED_TO`, and
`CONTRIBUTED` statements. It reads paths and allowed contributor formats from
`k-graph.toml`; it does not connect to a database.

The generated Cypher is derived. Regenerate it rather than editing it.
