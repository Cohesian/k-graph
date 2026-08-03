# Contributors

K accepts proposals from a closed contributor set:

$$
C=\{\texttt{research},\texttt{studio}\}
$$

| Contributor | Work |
|---|---|
| `research` | Research structure and formats such as `md` and `ipynb` |
| `studio` | Visual structure and formats such as `py`, `mp4`, and `youtube` |

Contributors are trusted by Cohesian but remain outside K's responsibility
boundary. They own their work and persistence. K owns the accepted graph.

## Node relation

Contributor attribution is a separate graph overlay:

$$
E_c\subseteq C\times V
$$

The relation associates a contributor with a K node. Its format set declares
which content forms that contributor supplies:

```yaml
contributors:
  research:
    - md
  studio:
    - py
    - mp4
```

An empty list records a structural contribution without a content body:

```yaml
contributors:
  research: []
```

A node can have no contributor, one contributor, or several contributors.
Contributor edges never affect TLF grouping, linear traversal, related
knowledge, canonical paths, or layout.

This node-local relation is a summary. An accepted-proposal history can later
record which properties and relationships each proposal changed.

## Boundary

Each contributor works in its own domain and adapts proposed work to K's
accepted proposal domain:

$$
a_c:D_c\rightharpoonup O_K
$$

The mapping is partial because not every internal result must be proposed or
has a valid TLF expression. It should be called a functor only after the
relevant structures and preservation laws are defined.

K does not resolve contributor storage itself. Research exposes its owned
storage through the `research-storage` CLI. A single object can be discovered
or resolved by immutable node `id` or current rooted `path`, together with a
format:

```bash
research-storage list --id <id> --format md --json
research-storage resolve --path <path> --format md --source local --json
```

The complete Research inventory is available in one call:

```bash
research-storage audit --json
```

This bulk response can be joined to K nodes by UUID without invoking the
contributor once per node. Contributors may organize storage by either
selector, while `id` remains valid when a graph reorganization changes paths.
Storage roots, credentials, and publication maps remain outside K.

The pending discovery and resolution boundary is laid out in
[`ROADMAP.md`](ROADMAP.md).

Contributors outside the current set require an explicit registry change.
