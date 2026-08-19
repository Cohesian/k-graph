# Resource overlay

TLF defines the topology of accepted knowledge. The resource overlay records
which contributor-owned content is accepted for each K node without turning
storage locations into graph topology.

## Separation from TLF

Let the accepted K graph be:

$$
G_{\mathcal K}
=
(V,E_g\sqcup E_l\sqcup E_r,\iota,\kappa,\mu)
$$

Its edge families express grouping, linear order, and semantic relation. They
do not express contributed content or physical storage.

Let:

$$
C=\{\texttt{research},\texttt{studio}\}
$$

be the current contributor registry, $D_c$ the domains owned by contributor
$c$, and $F$ the set of logical content formats. K's accepted resource
relation is:

$$
P_{\mathcal K}
\subseteq
\bigcup_{c\in C}(V\times\{c\}\times D_c\times F)
$$

Each element is one logical resource leaf:

$$
\rho=(v,c,d,f)
$$

It says that contributor $c$ provides format $f$ in domain $d$ for K node
$v$. The resource leaf belongs to this overlay. It is not necessarily a TLF
`F` node and it does not add a `GROUPS`, `NEXT`, or `RELATED_TO` edge.

## Identity and selection

The durable identity of a resource is:

$$
(\operatorname{id}(v),c,d,f)
$$

Protocol version 1 permits at most one logical resource for a given tuple. A
second store is a replica of that resource, not a second resource.

A consumer selects the K node by immutable id, rooted path, or both:

$$
\sigma
\in
\Sigma
=
I\sqcup P\sqcup(I\times P)
$$

and forms the complete target:

$$
\tau=(\sigma,(c,d,f))
$$

The id survives graph reorganization. The rooted path is human-readable and
revision-relative. When both are supplied, they must identify the same node.

## Node-local expression

The Directory projection uses the domain-aware form:

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

Here, `(contributor, domain)` is the ownership namespace and `format` selects
the logical leaf. Nodes without accepted resources use `contributors: {}`.
Proposal provenance is a separate concern and is not represented by empty
resource declarations.

## Stores and replicas

Contributors own persistence. For contributor $c$, explicit bindings relate
domains, stores, and formats:

$$
B_c\subseteq D_c\times S_c\times F
$$

For a resource $\rho$, the available physical locations are:

$$
\operatorname{Rep}(\rho)\subseteq S_c\times U
$$

where $U$ is the URI space. Local files and GitHub may be projected from a
rooted path or UUID. Google Drive and YouTube may require contributor-owned
maps. These are storage strategies; they do not alter $\rho$.

A logical format need not be one file extension. Studio registers
`loci-project` because an accepted scene resource is a self-contained project
directory; its internal `scene.toml` identifies the `.py` entrypoint. Every
store location for that resource therefore addresses the project boundary.

K stores the accepted relation $P_{\mathcal K}$. Each contributor stores its
domains, store descriptors, bindings, inventories, and credentials under its
own rules. Credentials never enter K or the declarative protocol.

## Tether

[Tether](../../tether/README.md) is the common bridge between a K target
$\tau$ and contributor-owned store declarations. It reads a contributor's
`contributor.toml` and route inventories to:

- validate the contributor package;
- discover resources and available stores;
- project targets to URIs; and
- identify targets from known URIs.

These resolution operations perform no download, upload, or graph mutation.
Tether also offers an explicit `pull` operation that a consumer may use to
materialize one selected store as a rooted-path directory or URI map. The
result is a consumer snapshot; it does not mutate K or contributor storage.
Proposal support may later prepare or submit resource-registration requests,
but K continues to validate and accept every change to $P_{\mathcal K}$.

## Invariants

- TLF topology and resource registration are distinct relations.
- Every resource belongs to one registered contributor and one of its domains.
- `(id, contributor, domain, format)` is durable resource identity.
- Stores are replicas or locations, not resource identities.
- Contributors own persistence; K owns accepted registration.
- Tether interprets the shared bridge protocol without taking ownership from
  K or contributors.

Contributor responsibilities are summarized in
[`CONTRIBUTORS.md`](CONTRIBUTORS.md). The complete declarative file contract is
in [Tether's contributor protocol](../../tether/docs/CONTRIBUTOR-PROTOCOL.md).
