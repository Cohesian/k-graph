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

Validation covers UUID identities, intrinsic fields, registered contributors,
typed resource hierarchies and keys, protocols and SHA-256 digests, grouping
coverage and reachability, linear reciprocity and degree, and related targets.

## Generate Neo4j Cypher

```bash
.venv/bin/kgraph-to-neo4j --out storage/neo4j/k-graph.cypher
```

The command emits `KNode`, `Contributor`, `GROUPS`, `NEXT`, `RELATED_TO`, and
resource-level `PROVIDES` statements. It reads persistence paths and registered
contributors from `k-graph.toml`; it does not connect to a database.

The generated Cypher is derived. Regenerate it rather than editing it.
