# Resource overlay

TLF defines accepted knowledge topology. The resource overlay records which
contributor-owned resources K accepts at each node without turning content or
storage locations into graph topology.

## Address

Let the accepted graph be:

$$
G_{\mathcal K}=(V,E_g\sqcup E_l\sqcup E_r,\iota,\kappa,\mu).
$$

A caller selects a node by immutable id, current rooted path, or both:

$$
\sigma\in I\sqcup P\sqcup(I\times P).
$$

For contributor $c$, finite non-empty hierarchy $H$, and local resource key
$p$, the selectable resource address is:

$$
a=(\sigma,c,H,p).
$$

Its durable identity uses the node UUID:

$$
\bar a=(\operatorname{id}(v),c,H,p).
$$

The hierarchy categorizes contributor ownership; it need not mirror K's
grouping tree or a physical directory. The resource key is unique inside one
$(v,c,H)$ namespace and is not necessarily a filename or extension.

## Acceptance and location

K stores:

$$
K(\bar a)=(q,z),
$$

where $q$ is a versioned resource protocol and $z$ its canonical SHA-256.
The contributor separately exposes locations:

$$
L_c(\bar a)=\{s\mapsto\lambda_s\}.
$$

Thus protocol and digest are accepted registry facts; bytes, stores,
credentials, and location descriptors remain contributor-owned. A protocol
defines whether the resource is a file or bounded tree and exactly how its
digest is computed.

## Node-local expression

```yaml
contributions:
  c_research:
    h_documents:
      r_md:
        protocol: markdown-bundle@1
        sha256: 7e40c9a693f4c3b118ed77c250f0dc037f291f2141f438abe7bda7e270e74b13
```

This accepted record is neither a TLF node nor an edge in $E_g$, $E_l$, or
$E_r$. Nodes with no accepted resources use `contributions: {}`.

## Exact replicas and publications

An exact location must reproduce the accepted digest under protocol $q$:

$$
\operatorname{SHA256}_q(\lambda_s)=z.
$$

A publication may transform the accepted bytes—for example, YouTube may
transcode an MP4. It remains linked to the accepted resource but does not
claim byte identity.

## Tether and consumers

[Tether](../../tether/README.md) reads contributor inventories to validate
resources, compare them with K, discover locations, and resolve selected
addresses. It owns neither K nor contributor persistence.

A consumer may derive an enriched snapshot:

$$
\widetilde G=G_{\mathcal K}\Join_{\operatorname{id}(v)}I_c.
$$

Layouts grouped by contributor, hierarchy, protocol, or store are projections
of that join. They are useful consumer views, not new authoritative graphs.

The complete grammar and protocol boundary are defined in
[`RESOURCE-CONTRACT-V2.md`](RESOURCE-CONTRACT-V2.md).
