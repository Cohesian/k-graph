# Directory projection

## 1. Meaning

The Directory Projection expresses the TLF graph with directories and YAML.
It is human-readable, Git-versioned, and composed from node-local declarations.

The complete projection lives in:

```text
storage/local/
```

## 2. Composite and leaf correspondence

```text
storage/local/
├── props.yaml
├── T-topic/
│   ├── props.yaml
│   ├── L-lecture/
│   │   ├── props.yaml
│   │   └── F-file.yaml
│   └── T-nested-topic/
│       └── props.yaml
└── F-direct-file.yaml
```

`T` and `L` are composites represented by directories containing
`props.yaml`. They may group any TLF kind. `F` and `Fd` are leaves represented
by YAML files.

The root is `storage/local/props.yaml`; its rooted path is `K` and its kind
is `T`.

## 3. Node declaration

Every node declares its intrinsic semantics:

```yaml
title: TLF Composite
description: Topic / Lecture / File composite pattern for a knowledge corpus.
kind: F
id: 42292902-3874-4d54-87ec-0e1b7362af13
```

The current projection stores `kind` explicitly and verifies it against the
directory or filename prefix. A different projection may derive the kind, but
the semantic value is always present in the graph model.

`id` is an immutable UUID. The directory name or YAML filename stem is the
local id. The rooted `path` is derived from the relative grouping path, for
example:

```text
T-computer-science/L-composite/F-04-TLF-composite
```

## 4. Resource declaration

Accepted contributor resources are local to the node:

```yaml
contributors:
  research:
    documents:
      - md
  studio:
    scenes:
      - loci-project
    videos:
      - mp4
```

Contributor keys, domain keys, and formats must be admitted by `k-graph.toml`.
Nodes without accepted resources use:

```yaml
contributors: {}
```

Proposal provenance, contributor storage locations, and URI resolution are not
encoded here.

## 5. Local edges

Each node declares its local view of the three edge families:

```yaml
edges:
  g: []
  l:
    prev: null
    next: null
  r: []
```

### Grouping

For a composite, `edges.g` lists its immediate children in authored order:

```yaml
edges:
  g:
    - F-01-carbon-binder
    - F-02-type-binder
  l:
    prev: null
    next: null
  r: []
```

Directory containment identifies possible children; `edges.g` selects and
orders them. Every immediate directory child appears exactly once.

### Linear

`edges.l` gives at most one previous and one next node:

```yaml
l:
  prev: F-01-function
  next: F-03-function-network
```

Reciprocal declarations must agree. Together they represent one directed
`NEXT` relationship. A sibling may be named by local id; a node elsewhere in
the graph is named by its rooted path.

### Related

`edges.r` lists directed non-structural relations. A simple target may be
written as a string; a weighted relation may be written as a mapping:

```yaml
r:
  - F-other
  - target: T-neighbor
    weight: 0.72
```

Related edges may fan out or cycle and do not affect grouping.
As with linear edges, cross-group targets use their rooted paths.

## 6. Local knowledge and global emergence

A node's local declaration contains:

- its intrinsic `kind`, `title`, and `description`;
- its accepted resources by contributor, domain, and format; and
- its incoming/outgoing neighborhood as expressed through `g`, `l`, and `r`.

Some incoming facts are declared reciprocally or by a neighboring composite,
then become visible after the local declarations are composed. The loader:

1. discovers every composite and leaf;
2. validates immutable UUID ids and derives rooted paths;
3. resolves local edge references;
4. validates the TLF and contributor laws; and
5. composes the complete graph.

Formally, for each edge family $x\in\{g,l,r\}$:

$$
E_x=\bigcup_{v\in V}E_x^+(v)
$$

No individual YAML node contains the whole graph.

## 7. Structural laws

- `T` and `L` nodes are composites; `F` and `Fd` nodes are leaves.
- Leaves have no outgoing grouping edges.
- Every non-root node has exactly one grouping parent.
- The grouping projection is rooted, ordered, and acyclic.
- Sibling order comes from `edges.g`, never alphabetical order.
- Each node has at most one incoming and one outgoing linear edge.

## 8. Representation summary

| TLF concept | Directory expression |
|---|---|
| Root `K` | `storage/local/props.yaml` |
| Topic | `T-*/props.yaml` |
| Lecture | `L-*/props.yaml` |
| File | `F-*.yaml` |
| Draft File | `Fd-*.yaml` |
| Stable identity | `id` UUID property |
| Intrinsic semantics | `kind`, `title`, `description` |
| Resource overlay | `contributors.<contributor>.<domain>[]` |
| Grouping | containment + ordered `edges.g` |
| Linear | `edges.l.prev` / `edges.l.next` |
| Related | `edges.r` |
| Rooted address | relative path from `storage/local/` |
