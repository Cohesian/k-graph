# TLF: formal model

## 1. Purpose

TLF—Topic, Lecture, File—is Cohesian's labeled composite pattern for a
knowledge corpus.

Its central distinction is:

```text
T and L are composites.
F and Fd are leaves.
```

The familiar shape:

```text
T -> L -> F
```

is common pedagogy, not a required depth hierarchy. A Topic or Lecture can
contain any mixture of Topics, Lectures, Files, and draft Files.

The graph has three edge families:

- `g`: grouping and structural shape;
- `l`: linear reading or traversal; and
- `r`: related knowledge.

Only `g` defines structural shape and layout. `l` and `r` are
orthogonal overlays on the same nodes.

## 2. Corpus

Let:

$$
\mathcal K
$$

be the knowledge corpus. Its full graph is:

$$
G_{\mathcal K}
=
\left(
V,\;
E_g \sqcup E_l \sqcup E_r,\;
\kappa,\;
\mu
\right)
$$

where:

- $V$ is the node set;
- $E_g$, $E_l$, and $E_r$ are disjoint relationship families;
- $\kappa$ assigns node kind;
- $\mu$ assigns local descriptive metadata.

The disjoint-union symbol distinguishes relationship meaning. The same ordered
pair of nodes can, in principle, be connected by more than one edge family.

## 3. Node kinds

The kind function is:

$$
\kappa:
V
\longrightarrow
\{T,L,F,F_d\}
$$

with inverse images:

$$
V_T=\kappa^{-1}(T)
\qquad
V_L=\kappa^{-1}(L)
$$

$$
V_F=\kappa^{-1}(F)
\qquad
V_{F_d}=\kappa^{-1}(F_d)
$$

Define composites:

$$
V_C=V_T\cup V_L
$$

and leaves:

$$
V_\ell=V_F\cup V_{F_d}
$$

The draft mark changes publication state, not structural role:

$$
F_d : \text{leaf}
$$

### Labels, not levels

`T`, `L`, `F`, and `Fd` are node labels. They are not fixed depth numbers.

Therefore all of these are valid under grouping:

```text
T[T]
T[L]
T[F]
L[T]
L[L]
L[F]
```

and a File remains a leaf:

```text
F[]
Fd[]
```

## 4. Composite grammar

The recursive grammar is:

$$
K
::=
F
\mid
F_d
\mid
c[K_1,\ldots,K_n]
\qquad
c\in\{T,L\}
$$

Equivalently:

$$
F:K
\qquad
F_d:K
$$

and:

$$
c[X_1,\ldots,X_n]:K
\quad
c\in\{T,L\}
\quad
X_i:K
$$

Both composite kinds admit the same child universe:

$$
\operatorname{child}_g(T),
\operatorname{child}_g(L)
\subseteq
V
$$

while:

$$
\operatorname{child}_g(F)
=
\operatorname{child}_g(F_d)
=
\varnothing
$$

This is the TLF composite law:

$$
T,L:K^*\to K
$$

### Identity and rooted address

Each node will have an immutable identity:

$$
\iota:V\to I
$$

with $\iota$ injective. Separately, an accepted grouping projection derives a
rooted address:

$$
\operatorname{path}_g:V\to\operatorname{Path}
$$

Because the current grouping profile is a rooted arborescence, every node has
exactly one such path in a graph revision. A regrouping may change
$\operatorname{path}_g(v)$ while $\iota(v)$ remains fixed.

Thus `id` answers *which node?* and `path` answers *where is that node in this
grouping projection?* Either may select a node; when both are supplied they
must agree. The current Neo4j property named `key` is a serialization of this
rooted path, not a separate identity.

## 5. Local knowledge

Every node has three intrinsic semantic properties:

$$
\nu(v)
=
\left(
\kappa(v),
\operatorname{title}(v),
\operatorname{description}(v)
\right)
$$

The kind $\kappa(v)$ is always present in the mathematical object. A concrete
representation may store it explicitly or derive it from a label, path, or
type marker.

Title and description are the node's concise semantic surface. They identify
and describe the concept; they are not the complete paper, scene, or video
body.

Equivalently, the descriptive component is:

$$
\mu(v)
=
\left(
\operatorname{title}(v),
\operatorname{description}(v)
\right)
$$

The node's local TLF neighborhood is:

$$
\operatorname{loc}_{TLF}(v)
=
\left(
\nu(v),
E_g^-(v),E_g^+(v),
E_l^-(v),E_l^+(v),
E_r^-(v),E_r^+(v)
\right)
$$

where $E_x^-$ and $E_x^+$ are the incoming and outgoing incidences for edge
family $x$.

The edges are not intrinsic node properties. They belong to the graph, while
their incidences form the node's local view.

### Contributor overlay

Contributor attribution is separate from TLF topology. The current contributor
set is:

$$
C
=
\{\texttt{research},\texttt{studio}\}
$$

Define the contributor relation:

$$
E_c\subseteq C\times V
$$

and the format declaration:

$$
\phi:E_c\to\mathcal P(\mathcal F)
$$

where initially:

$$
\mathcal F
=
\{\texttt{md},\texttt{ipynb},\texttt{py},\texttt{mp4},\texttt{youtube}\}
$$

For $(c,v)\in E_c$, contributor $c$ has an accepted contribution associated
with node $v$. The set $\phi(c,v)$ names the contributed content formats.

An empty format set is meaningful:

$$
\phi(c,v)=\varnothing
$$

means that $c$ contributed to the node or its structure without contributing a
content body.

A node may receive work from several contributors:

$$
\deg_c^-(v)\geq0
$$

The contributor overlay does not change grouping, reading order, related
knowledge, canonical paths, or layout.

The complete local registry view is therefore:

$$
\operatorname{loc}(v)
=
\left(
\nu(v),
E_g^-(v),E_g^+(v),
E_l^-(v),E_l^+(v),
E_r^-(v),E_r^+(v),
E_c^-(v),
\phi|_{E_c^-(v)}
\right)
$$

In the Directory Projection, this neighborhood is declared locally in YAML.
In the Neo4j Projection, node properties and incident relationships are stored
explicitly by the graph engine. The mathematical locality is unchanged even
though the representation changes.

The contributor relation is a node-level summary. Exact attribution of a
property or relationship change can live in a future accepted-proposal
history.

## 6. Emergence

The corpus is composed from local nodes and compatible relationships:

$$
V
=
\bigcup_{v\in V}\{v\}
$$

$$
E_x
=
\bigcup_{v\in V}E_x^+(v)
\qquad
x\in\{g,l,r\}
$$

A relationship is valid only when its endpoints resolve to admitted nodes.
Global properties then emerge:

- root reachability;
- grouping ancestry and descendants;
- canonical paths;
- reading chains;
- related neighborhoods;
- Topic and Lecture forests;
- scoped views;
- backlinks; and
- structural layout.

No node needs to contain the complete corpus. It needs only its own properties
and valid relationships to neighboring nodes.

This is the local-to-global principle:

$$
\text{local node knowledge}
+
\text{compatible adjacency}
\Longrightarrow
\text{global k-graph}
$$

## 7. Grouping axis

The grouping projection is:

$$
G_g=\pi_g(G_{\mathcal K})=(V,E_g)
$$

with:

$$
E_g\subseteq V_C\times V
$$

A grouping edge means containment:

$$
(u,v)\in E_g
\Longleftrightarrow
u\text{ directly groups }v
$$

The distinguished root is:

$$
\rho=K
$$

represented by a Topic node.

The Cohesian storage profile requires:

$$
\operatorname{par}_g(\rho)=\varnothing
$$

and:

$$
\left|\operatorname{par}_g(v)\right|=1
\qquad
v\neq\rho
$$

with every node reachable from $\rho$ and no grouping cycle. Therefore:

$$
G_g
\text{ is a rooted arborescence}
$$

and consequently:

$$
G_g
\text{ is a DAG}
$$

The more general mathematical family can admit a rooted DAG with shared
children. The current Cohesian profile chooses one parent so every node has one
canonical grouping path.

### Authored order

Grouping order is a function:

$$
\omega:E_g\to\mathbb N_0
$$

For every parent $u$, positions are unique among its outgoing grouping edges:

$$
(u,v_i)\neq(u,v_j)
\Longrightarrow
\omega(u,v_i)\neq\omega(u,v_j)
$$

The value is stored zero-based. Human display indexes may add one.

Directory enumeration and alphabetical sorting do not define $\omega$.

## 8. Linear axis

The target linear family is:

$$
E_l\subseteq V\times V
$$

This generalizes the original Foundations paper, which used only
$V_\ell\times V_\ell$. Topics, Lectures, Files, and draft Files may all
participate in linear traversal.

The stored direction is:

$$
u\xrightarrow{\operatorname{NEXT}}v
$$

From $u$, the edge is `next`. From $v$, the same physical relationship is
`prev`.

The local degree law is:

$$
\deg_l^+(v)\leq1
\qquad
\deg_l^-(v)\leq1
$$

So a node can have at most two linear incidences: one previous and one next.
Linear traversal does not branch.

For the initial Cohesian profile, a linear component is a finite directed path.
Cycles are rejected:

$$
G_l=(V,E_l)
\text{ is acyclic}
$$

## 9. Related axis

The related family is:

$$
E_r\subseteq V\times V
$$

and may connect any node kinds.

A weight is an optional function:

$$
w:E_r\rightharpoonup\mathbb R
$$

An edge outside the domain of $w$ is related but unscored. Until a normalized
scale is accepted, consumers must preserve the value without assuming that
zero, one, or any other number has a universal meaning.

Related edges:

- may fan out;
- may cross grouping boundaries;
- may cycle;
- preserve direction; and
- do not affect structural position.

## 10. Shape and fixed-node law

Only grouping defines the taken structural shape:

$$
\operatorname{shape}(\mathcal K)
=
(V,E_g)
$$

Let:

$$
p:V\to\mathbb R^2
$$

be a graph layout. The fixed-node law is:

$$
p
=
\operatorname{layout}(V,E_g)
$$

so:

$$
\operatorname{layout}(V,E_g,E_l,E_r)
=
\operatorname{layout}(V,E_g)
$$

Therefore:

$$
\Delta(E_l\cup E_r)
\not\Rightarrow
\Delta p
$$

Adding a reading or related relationship does not reposition nodes. Regrouping
a node may.

## 11. Primary edge projections

Grouping:

$$
\pi_g(G_{\mathcal K})
=(V,E_g)
$$

Linear:

$$
\pi_l(G_{\mathcal K})
=(V_l,E_l)
$$

where $V_l$ is the set of linear endpoints.

Related:

$$
\pi_r(G_{\mathcal K})
=(V_r,E_r,w)
$$

where $V_r$ is the set of related endpoints.

Combined traversal:

$$
\pi_{lr}(G_{\mathcal K})
=
(V_l\cup V_r,E_l\sqcup E_r,w)
$$

These are views of one corpus:

$$
\pi_g,\pi_l,\pi_r
:
G_{\mathcal K}
\longrightarrow
\text{projections}
$$

They are not separate corpora.

The structural orthogonality law is:

$$
\pi_g\perp\pi_l,\pi_r
$$

meaning $E_l$ and $E_r$ can change while $E_g$ remains fixed.

## 12. Topic forest

Topics can serve as scoped view origins.

Define strict grouping ancestry:

$$
u\prec_gv
$$

when a non-empty directed grouping path exists from $u$ to $v$.

Topic adjacency is:

$$
(T_a,T_b)\in E_T
$$

iff:

$$
T_a\prec_gT_b
$$

and no Topic lies strictly between them:

$$
\nexists T_c\in V_T:
T_a\prec_gT_c\prec_gT_b
$$

Then:

$$
\pi_T(G_{\mathcal K})
=(V_T,E_T)
$$

is the Topic forest. It hides Lectures and Files while preserving immediate
Topic ancestry.

## 13. Lecture forest

Lecture adjacency is defined analogously:

$$
(L_a,L_b)\in E_L
$$

iff:

$$
L_a\prec_gL_b
$$

and:

$$
\nexists L_c\in V_L:
L_a\prec_gL_c\prec_gL_b
$$

Thus:

$$
\pi_L(G_{\mathcal K})
=(V_L,E_L)
$$

is the Lecture forest. It provides a corpus-wide Lecture index without
requiring every Lecture to expand recursively.

## 14. Bounded Topic view

Fix:

$$
T_0\in V_T
$$

The current Foundations view expands all Lectures until a File or nested Topic.
The target bounded view is intentionally shallower:

- a File or draft File is shown and stops;
- a nested Topic is shown as a portal and stops;
- the first encountered Lecture layer expands; and
- a Lecture below another Lecture is shown as a portal and stops.

Let:

$$
\operatorname{between}_{T_0}(x)
$$

be the strict grouping ancestors of $x$ below $T_0$. Define:

$$
\operatorname{stop}_{T_0}(x)
\Longleftrightarrow
x\in V_\ell
$$

or:

$$
x\in V_T\land x\neq T_0
$$

or:

$$
x\in V_L
\land
\exists a\in\operatorname{between}_{T_0}(x):
a\in V_L
$$

A stop node remains visible, but its children do not.

The visible set contains $T_0$ and every descendant with no strict stop
ancestor below $T_0$:

$$
V_{T_0}
=
\left\{
x\in\operatorname{desc}_g(T_0)\cup\{T_0\}
\mid
\nexists a:
T_0\prec_ga\prec_gx
\land
\operatorname{stop}_{T_0}(a)
\right\}
$$

and:

$$
E_{g,T_0}
=
E_g\cap(V_{T_0}\times V_{T_0})
$$

Therefore:

$$
\pi_{T_0}(G_{\mathcal K})
=(V_{T_0},E_{g,T_0})
$$

## 15. Bounded Lecture view

Fix:

$$
L_0\in V_L
$$

The Lecture view shows the origin, direct Files, and the first nested
composites as portals. Define:

$$
\operatorname{stop}_{L_0}(x)
\Longleftrightarrow
x\in V_\ell
$$

or:

$$
x\in V_T
$$

or:

$$
x\in V_L\land x\neq L_0
$$

Using the same visible-set construction:

$$
\pi_{L_0}(G_{\mathcal K})
=(V_{L_0},E_{g,L_0})
$$

This view gives a Lecture its own description and bounded neighborhood without
recursively opening a nested Lecture or Topic.

## 16. File view

For:

$$
f\in V_\ell
$$

the File view combines:

- the node's local metadata and data declarations;
- its root-to-node grouping path;
- its incoming `prev` and outgoing `next`;
- related outgoing and incoming neighbors;
- resolved research and media;
- backlinks; and
- a bounded grouping context.

Its closest Topic anchor is:

$$
\operatorname{anchor}_T(f)
=
\max_{\prec_g}
\{t\in V_T\mid t\preceq_gf\}
$$

Its closest Lecture anchor is defined analogously when one exists.

## 17. Canonical paths and indexes

Because every non-root node has one grouping parent, every node has one root
path:

$$
\rho=v_0\to v_1\to\cdots\to v_n=v
$$

Let $\lambda(v)$ be the node's local id. Then:

$$
\operatorname{gpath}(v)
=
\lambda(v_1)/\cdots/\lambda(v_n)
$$

with:

$$
\operatorname{gpath}(\rho)=K
$$

This path is the current portable content key. Moving or renaming a node is an
explicit key migration.

The grouping index is:

$$
\operatorname{gindex}(v)
=
\left(
\omega(v_0,v_1)+1,\ldots,\omega(v_{n-1},v_n)+1
\right)
$$

It is a display coordinate, not identity.

## 18. Representation independence

TLF does not require a filesystem, YAML, Neo4j, or a particular website.

The formal object is:

$$
G_{\mathcal K}
$$

Possible representations include:

- a directory/YAML projection;
- a Neo4j property graph;
- a generated JSONL, CSV, or Cypher snapshot;
- a static Site catalog; and
- a visual layout.

A representation is faithful when it preserves the laws relevant to its
projection.

## 19. Compressed laws

Corpus:

$$
\boxed{
G_{\mathcal K}
=
(V,E_g\sqcup E_l\sqcup E_r,\kappa,\mu)
}
$$

Contributor overlay:

$$
\boxed{
E_c\subseteq C\times V,
\qquad
\phi:E_c\to\mathcal P(\mathcal F)
}
$$

Composite grammar:

$$
\boxed{
K::=F\mid F_d\mid c[K_1,\ldots,K_n],
\quad c\in\{T,L\}
}
$$

Shape:

$$
\boxed{
\operatorname{shape}(\mathcal K)=(V,E_g)
}
$$

Linear degree:

$$
\boxed{
\deg_l^-(v)\leq1
\quad\land\quad
\deg_l^+(v)\leq1
}
$$

Projection:

$$
\boxed{
\pi_g,\pi_l,\pi_r
\text{ are views of one corpus}
}
$$

Local emergence:

$$
\boxed{
\text{local knowledge}
+
\text{valid adjacency}
\Longrightarrow
\text{global k-graph}
}
$$
