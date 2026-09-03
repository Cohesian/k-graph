# Resource contract v2

Status: **active**

This document defines the active semantic contract for accepted resources in
K. The Directory projection, Neo4j generator, validator, and Research
inventory implement this contract.

## 1. Separation of concerns

Let the accepted knowledge graph be:

$$
G_{\mathcal K}
=
(V,E_g\sqcup E_l\sqcup E_r,\iota,\kappa,\mu).
$$

The graph owns knowledge-node identity, intrinsic semantics, and topology.
Resources form a separate node-local overlay. Registering a resource does not
create an edge in $E_g$, $E_l$, or $E_r$, and a resource is not a knowledge
node kind.

Four authorities remain distinct:

| Authority | Owns |
|---|---|
| K | accepted resource address, protocol, and digest |
| contributor | resource bytes and physical locations |
| Tether | protocol interpretation, hashing, validation, and resolution |
| consumer | presentation, composition, and materialized layout |

K does not store contributor credentials or physical URIs. A contributor does
not own K topology. Tether does not become a persistence authority. A consumer
may derive a snapshot without changing any of the three upstream authorities.

## 2. Node selector

A consumer may select a knowledge node by immutable UUID, current rooted path,
or both:

$$
\sigma
\in
\Sigma
=
I\sqcup P\sqcup(I\times P).
$$

When both selectors are present, they must identify the same node. The UUID is
the durable identity. The rooted path is a revision-relative address derived
from the accepted grouping projection.

## 3. Contributor hierarchy

Let $C_{\mathcal K}$ be K's registered contributor set. For contributor $c$,
let $D_c$ be its hierarchy-segment vocabulary. A resource hierarchy is a
finite non-empty sequence:

$$
H=(h_1,\ldots,h_n)\in D_c^+.
$$

This permits arbitrary depth without fixing a universal domain tree. Examples
are:

$$
(\texttt{documents})
$$

and:

$$
(\texttt{media},\texttt{videos}).
$$

The hierarchy categorizes contributor ownership. It is not required to mirror
K topology or physical directories.

## 4. Resource key and address

For one selected node, contributor, and hierarchy, $p$ is a local resource
key. The complete query address is:

$$
a=(\sigma,c,H,p).
$$

Its durable logical identity replaces $\sigma$ with the immutable K node id:

$$
\bar a=(\operatorname{id}(v),c,H,p).
$$

The key $p$ is not necessarily a filename or extension. It distinguishes one
accepted resource inside the namespace $(v,c,H)$. The protocol defines the
resource's concrete shape.

There is at most one accepted resource for each $\bar a$. Several physical
locations may expose the same accepted resource.

## 5. Accepted record

K stores the acceptance record:

$$
K(\bar a)=(q,z),
$$

where:

- $q$ is a versioned protocol id such as `markdown-bundle@1`; and
- $z$ is the lowercase SHA-256 digest produced by that protocol.

The protocol determines the resource boundary, required structure,
canonical byte stream, and digest algorithm. Therefore a digest is meaningful
only together with its protocol id.

K does not store the resource's locations. The contributor exposes:

$$
L_c(\bar a)
=
\{s\mapsto\lambda_s\},
$$

where $s$ is a contributor-owned store id and $\lambda_s$ is a location
descriptor interpreted by Tether.

## 6. Typed YAML expression

The Directory projection serializes the address namespace with typed mapping
keys:

```yaml
contributions:
  c_research:
    h_documents:
      r_md:
        protocol: markdown-bundle@1
        sha256: 7e40c9a693f4c3b118ed77c250f0dc037f291f2141f438abe7bda7e270e74b13
```

An arbitrary-depth hierarchy is nested recursively:

```yaml
contributions:
  c_research:
    h_media:
      h_videos:
        r_primary:
          protocol: mp4-file@1
          sha256: 9c56cc51b374c3ba189210d5b6d4bf57790d351c96c47c02190ecf1e430635ab
```

The prefixes are representation-level type markers:

| Prefix | Meaning | Semantic value |
|---|---|---|
| `c_` | contributor | key without `c_` |
| `h_` | hierarchy segment | key without `h_` |
| `r_` | resource key | key without `r_` |

The grammar is:

```text
contributions := contributor*
contributor   := c_<id> -> hierarchy
hierarchy     := (h_<segment> -> hierarchy-or-resources)+
hierarchy-or-resources := hierarchy entries and/or resource entries
resource      := r_<key> -> { protocol, sha256 }
```

A hierarchy node may contain both nested `h_` entries and local `r_` entries.
Because resources are mapping keys, duplicate keys inside the same
$(v,c,H)$ namespace are structurally invalid. A node with no accepted
resources uses:

```yaml
contributions: {}
```

## 7. Protocol contract

A protocol id has the form:

```text
<name>@<positive-integer-version>
```

Every protocol definition must specify:

1. whether the resource is a file or bounded tree;
2. the required entrypoint or root structure;
3. included and rejected members;
4. canonical path and byte rules;
5. the SHA-256 procedure; and
6. the consumer-facing media or execution semantics.

Moving a resource to another store must not change its digest. Changing its
accepted bytes must change its digest. A protocol revision that changes the
canonicalization rules receives a new protocol version.

The initial protocol vocabulary and canonical hashing procedures are defined
by [Tether's protocol v2 specification](../../tether/docs/CONTRIBUTOR-PROTOCOL-V2.md).

## 8. Exact locations and publications

A contributor location has one of two relations to the accepted digest:

### Exact

An exact location claims that resolving and hashing its resource with protocol
$q$ yields $z$:

$$
\operatorname{SHA256}_q(\lambda_s)=z.
$$

Local files, GitHub raw content, and downloadable Drive content may satisfy
this relation.

### Publication

A publication is a transformed or hosted projection of the accepted resource.
For example, YouTube may transcode an accepted MP4. Its URI is useful to a
consumer but does not claim byte identity with $z$.

A publication location records `relation = "publication"` and identifies the
accepted digest from which it was produced. It cannot satisfy an exact digest
check unless the retrieved bytes independently match.

## 9. Production provenance

Production and contribution ownership are different relations. Protocol v2
has Research own accepted scientific resources. Studio is a
production workstation and may produce a resource later accepted under
`c_research`.

Optional metadata such as:

```toml
produced_by = "studio"
```

may preserve that provenance in the contributor inventory. It is not part of
$\bar a$, does not grant contributor authority, and does not replace proposal
history.

The registered contributor set remains extensible through explicit K
admission. No repository becomes a contributor merely by using Tether or by
producing compatible content.

## 10. Derived projections

Neither contributor inventories nor consumer snapshots duplicate K's
canonical topology. A consumer may derive an enriched graph:

$$
\widetilde G
=
G_{\mathcal K}
\Join_{\operatorname{id}(v)}
I_c,
$$

where $I_c$ is a contributor inventory. Views grouped by contributor,
hierarchy, protocol, store, or layout are projections of this join—not new
authoritative graphs.

## 11. Invariants

- K topology and resource acceptance are distinct relations.
- UUID is durable identity; rooted path is a checked, revision-relative
  selector.
- The complete resource identity is $(\operatorname{id}(v),c,H,p)$.
- A resource key is unique inside one $(v,c,H)$ namespace.
- K accepts `protocol` and `sha256`, never a mutable unverified location.
- A contributor owns bytes, stores, and location descriptors.
- An exact location must reproduce the accepted protocol digest.
- A publication must not be presented as an exact replica.
- Production provenance does not imply contributor ownership.
- Tether interprets the contract without owning K or contributor persistence.
- Consumer layouts and compositions are derived and non-authoritative.

## 12. Version boundary

Protocol v2 replaced the v1 identity:

$$
(\operatorname{id}(v),c,d,f)
$$

into:

$$
(\operatorname{id}(v),c,H,p).
$$

It also replaced format lists with named resources carrying a versioned
protocol and digest. Tether retains v1 parsing only as a compatibility path;
K's authored graph is entirely v2 and rejects mixed serialization.

The planned topology term `Entry` is independent of this contract. Renaming
TLF to TLE is a separate graph migration; a resource is never synonymous with
either a File or an Entry node.
