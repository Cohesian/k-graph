# Contributors

This document describes the active v1 contributor projection. Protocol v2's
accepted semantic target—including hierarchical domains, named resource keys,
protocols, digests, and the separation of Studio production from Research
ownership—is defined in
[`RESOURCE-CONTRACT-V2.md`](RESOURCE-CONTRACT-V2.md).

K accepts proposals from a closed contributor set:

$$
C=\{\texttt{research},\texttt{studio}\}
$$

| Contributor | Work |
|---|---|
| `research` | Research documents, document companions, executable studies, and study media |
| `studio` | Visual structure and formats such as `loci-project` and `mp4` |

Contributors are trusted by Cohesian but remain outside K's responsibility
boundary. They own their work and persistence. K owns the accepted graph.

## Accepted contribution relation

The canonical resource model is defined in
[`RESOURCE-OVERLAY.md`](RESOURCE-OVERLAY.md).

The domain-aware registration relation is:

$$
P_K\subseteq V\times C\times D\times F
$$

An element $(v,c,d,f)\in P_K$ states that K accepts contributor $c$ as a
provider of format $f$ in domain $d$ for node $v$:

```yaml
contributors:
  research:
    documents:
      - md
      - ipynb
      - companions
    code:
      - python-project
    media:
      - mp4
  studio:
    scenes:
      - loci-project
    videos:
      - mp4
```

The Directory and Neo4j projections preserve contributor, domain, and format
explicitly. `youtube` is therefore a store, not a format; a YouTube location
may expose a Studio `videos/mp4` resource.

## Logical resource leaf

Every accepted tuple identifies one logical resource:

$$
\rho=(v,c,d,f)
$$

Its durable key is:

$$
(\operatorname{id}(v),c,d,f)
$$

Protocol version 1 gives the resource no additional name. For one node,
contributor, domain, and format there is at most one logical resource. Several
stores may expose replicas of it.

A format may identify a bounded aggregate rather than one file extension.
For example, `research/documents/companions` identifies one directory of files
referenced by a node's document. The files inside that aggregate do not become
additional K resources or receive K node identities.

This is a leaf of the contributor overlay, not necessarily a TLF File. Any
`T`, `L`, `F`, or `Fd` node can have resources attached without changing TLF
topology.

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

K does not resolve contributor storage itself. Every contributor exposes one
localized `contributor.toml` containing independent domain and store axes plus
their explicit bindings. [Tether](../../tether/README.md) reads that file
directly; no contributor-specific bridge executable is required.

A target keeps the K selector separate from contribution semantics:

$$
\tau=(\sigma,(c,d,f))
$$

Thus $\tau$ is the selectable form of $\rho$. The contributor and domain
localize ownership; the format selects the resource leaf. Physical storage may
mirror `path`, use stable `id`, or use a provider-controlled map.

Research can therefore be projected by id, rooted path, domain, format, store,
or any intersection of those filters:

```bash
tether resource resolve ../research \
  --domain documents \
  --format md
```

The bulk response joins to K nodes by UUID without invoking the contributor
once per node. Contributors may organize inventories by either selector,
while `id` remains valid when a graph reorganization changes paths. Storage
roots, credentials, and publication maps remain outside K.

The remaining K-side migration is laid out in
[`ROADMAP.md`](ROADMAP.md).

The concrete contributor identity and inventory workflow is documented in
[Tether's onboarding guide](../../tether/docs/CONTRIBUTOR-ONBOARDING.md).

Contributors outside the current set require an explicit registry change.
