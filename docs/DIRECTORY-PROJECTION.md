# Directory projection

## 1. Meaning

The Directory Projection expresses a TLF k-graph with directories and YAML.

It is one concrete representation of the mathematical object defined in
[`TLF.md`](TLF.md). Its purpose is to make the graph:

- human-readable;
- locally editable;
- Git-versioned;
- structurally visible without a database UI; and
- composable from node-local declarations.

The projection lives in:

```text
k-graph/
```

## 2. Composite and leaf correspondence

Directories naturally express recursive composites:

```text
composite/
├── composite/
│   └── leaf
└── leaf
```

TLF labels those roles:

```text
k-graph/
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

`T` and `L` are composites. Either may contain any mixture of `T`, `L`, `F`,
and `Fd`. `F` and `Fd` are leaves.

## 3. Root

The distinguished root is:

```text
k-graph/props.yaml
```

Its graph key is `K`, and its kind is `T`:

```yaml
title: Knowledge
description: Root topic for the Cohesian k-graph.
kind: T
edges:
  g: []
  l:
    prev: null
    next: null
  r: []
```

## 4. Composite nodes

A Topic or Lecture is a directory whose local node declaration is
`props.yaml`:

```text
k-graph/T-computer-science/props.yaml
k-graph/T-computer-science/L-composite/props.yaml
```

Example:

```yaml
title: Composite
description: Binder patterns and the TLF corpus composite model.
kind: L
edges:
  g:
    - F-01-carbon-binder
    - F-02-type-binder
    - F-03-query-binder
    - F-04-TLF-composite
  l:
    prev: null
    next: null
  r: []
```

The directory name is the local id. `edges.g` names immediate children in
authored pedagogical order.

## 5. Leaf nodes

A File or draft File is a YAML file named by its local id:

```text
k-graph/T-computer-science/L-composite/F-04-TLF-composite.yaml
k-graph/T-computer-science/L-functions/Fd-function-orchestration.yaml
```

Example:

```yaml
title: TLF Composite
description: Topic / Lecture / File composite pattern for a knowledge corpus.
kind: F
data:
  documents:
    - md
  media:
    scripts:
      scenes:
        - py
    videos:
      - mp4
edges:
  g: []
  l:
    prev: F-03-query-binder
    next: null
  r: []
```

The filename stem is the local id. The id is data-agnostic: it does not contain
`.md`, `.py`, `.mp4`, or a provider name.

## 6. Local knowledge

Each YAML node knows only:

- its kind;
- title and description;
- abstract data representations when present; and
- its local `g`, `l`, and `r` declarations.

Topology is not placed inside `data`. `data` describes associated research and
media forms; `edges` describes graph adjacency.

The three local edge axes are:

```yaml
edges:
  g: []
  l:
    prev: null
    next: null
  r: []
```

### Grouping

`edges.g` lists the composite's immediate children in order.

The directory contains the possible child nodes. The YAML declaration selects
and orders them:

$$
\operatorname{children}_g(c)
=
\operatorname{edges.g}(c)
$$

### Linear

`edges.l` gives zero or one previous and zero or one next node:

```yaml
l:
  prev: F-01-function
  next: F-03-function-network
```

The two declarations describe the local position of a node in a linear walk.
Reciprocal declarations must agree.

### Related

`edges.r` lists non-structural related nodes:

```yaml
r:
  - F-other
```

Related declarations may fan out or cycle and never alter directory grouping.

## 7. Global emergence

The complete graph emerges by loading every local node and resolving its
references:

$$
V
=
\bigcup_v\{v\}
$$

$$
E_x
=
\bigcup_v E_x^+(v)
\qquad
x\in\{g,l,r\}
$$

No YAML file contains the entire corpus. Each node carries only its local
description and adjacency.

The loader:

1. walks the directory tree;
2. registers each `props.yaml` and leaf YAML;
3. derives the node's graph key from its relative path;
4. resolves local edge targets;
5. validates reciprocal and structural laws; and
6. composes the global TLF graph.

## 8. Paths

For:

```text
k-graph/T-computer-science/L-composite/F-04-TLF-composite.yaml
```

the local components are:

```text
T-computer-science
L-composite
F-04-TLF-composite
```

and the graph key is:

```text
T-computer-science/L-composite/F-04-TLF-composite
```

The root key is `K`.

The same key can project into parallel content locations without adding a file
extension to node identity.

## 9. Data declarations

The present Directory Projection uses:

```text
data.documents
data.media.scripts.scenes
data.media.videos
```

Examples:

```yaml
data:
  documents:
    - md
    - ipynb
```

```yaml
data:
  media:
    scripts:
      scenes:
        - py
    videos:
      - mp4
```

These values declare representations, not physical locations. Concrete
locations are resolved through:

```text
k-graph.toml
maps/
```

Research-document bodies remain outside this index. Scene implementations and
rendered video bodies also remain outside it.

## 10. Structural laws

For a composite $c$:

$$
\kappa(c)\in\{T,L\}
$$

and:

$$
\operatorname{edges.g}(c)
\subseteq
\operatorname{children}_{dir}(c)
$$

Every immediate directory child is represented exactly once in `edges.g`.

For a leaf $f$:

$$
\kappa(f)\in\{F,F_d\}
$$

and:

$$
\operatorname{edges.g}(f)=\varnothing
$$

Every non-root node has one directory parent. Therefore the grouping
projection is a rooted tree and consequently a DAG.

Sibling order comes from `edges.g`, never alphabetical directory order.

## 11. Representation summary

| TLF concept | Directory expression |
|---|---|
| Root `K` | `k-graph/props.yaml` |
| Topic | `T-*/props.yaml` |
| Lecture | `L-*/props.yaml` |
| File | `F-*.yaml` |
| Draft File | `Fd-*.yaml` |
| Node metadata | YAML properties |
| Grouping | Directory containment + ordered `edges.g` |
| Linear | `edges.l.prev` / `edges.l.next` |
| Related | `edges.r` |
| Content declaration | `data` |
| Graph key | Relative path from `k-graph/` |
| Concrete content location | `k-graph.toml` + maps |
