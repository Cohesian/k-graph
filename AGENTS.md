# Cohesian k-graph — agent onboarding

Read this file before modifying node metadata, graph tooling, schemas, exports,
or resolver configuration.

## Purpose

This repository owns Cohesian's formal TLF model, complete Directory
Projection, Neo4j expression, and representation tooling.

It does not own:

- Markdown research bodies; those remain in `Cohesian/foundations`;
- Python scene implementations or video production; those remain in
  `Cohesian/studio`;
- public presentation; that belongs to `Cohesian/site`; or
- Cohesian's constitutional principles and identity; those belong to
  `Cohesian/core`.

## Read first

| Need | Read |
|---|---|
| Repository entry point | [`README.md`](README.md) |
| Formal TLF mathematics | [`docs/TLF.md`](docs/TLF.md) |
| Directory/YAML projection | [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) |
| Neo4j projection | [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) |
| Normative repository contract | [`CONTRACT.md`](CONTRACT.md) |
| Representation tooling | [`tools/README.md`](tools/README.md) |
| License boundaries | [`LICENSING.md`](LICENSING.md) |

## Representation boundary

The Directory Projection stores node-local metadata, content declarations, and
local graph edges:

```yaml
title: Function
description: Functions as bounded nodes and transformations.
kind: F
data:
  documents:
    - md
edges:
  g: []
  l:
    prev: null
    next: null
  r: []
```

The Neo4j Projection expresses the same local edges as `GROUPS`, `NEXT`, and
`RELATED_TO` relationships.

Never place topology inside `data`. Never place provider URLs, credentials,
database coordinates, or resolved local paths inside node YAML.

## Change boundary

- Preserve `T`, `L`, `F`, and `Fd` until a separate terminology decision is
  accepted.
- Treat the root `K` as a distinguished `T` node.
- Derive node identity from the node's relative path; do not add a duplicate
  YAML id field.
- Preserve equivalence between the Directory and Neo4j projections.
- Regenerate derived Cypher through the translator rather than editing it.
- Never add credentials, Aura secrets, tokens, or private Drive links.

## Validation

Create a local Python environment and install the YAML dependency:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Then validate the local Directory Projection without writing outputs:

```bash
.venv/bin/python tools/to_neo4j.py
.venv/bin/python tools/validate_kgraph.py
git diff --check
```

Any graph validation error is blocking.
