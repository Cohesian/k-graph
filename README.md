# Cohesian k-graph

`k-graph` is Cohesian's knowledge-index repository. It contains the formal TLF
model, a complete Directory Projection, the Neo4j property-graph expression,
and the tooling that translates between concrete representations.

The repository does not contain research-document bodies, scene
implementations, or rendered videos.

## Representations

| Concern | Expression |
|---|---|
| Representation-independent TLF | [`docs/TLF.md`](docs/TLF.md) |
| Git-friendly complete graph | [`k-graph/`](k-graph/) |
| Node and relationship property graph | Neo4j |
| Content path and URI resolution | [`k-graph.toml`](k-graph.toml) |
| Research Markdown | [`Cohesian/foundations`](https://github.com/Cohesian/foundations) |
| Scene code and video production | [`Cohesian/studio`](https://github.com/Cohesian/studio) |

The Directory and Neo4j projections express the same mathematical edge
families in different languages:

```text
Directory/YAML: edges.g / edges.l / edges.r
Neo4j:         GROUPS / NEXT / RELATED_TO
```

Topology never belongs inside a node's `data` declaration.

## Current status

The complete current Directory Projection, resolver configuration, and maps
have been copied from Foundations. Foundations remains unchanged.

The Neo4j translator validates that local graph and emits reviewable Cypher for
`cypher-shell`. No database has been changed yet.

## Read first

| Need | Read |
|---|---|
| Agent onboarding | [`AGENTS.md`](AGENTS.md) |
| Formal TLF mathematics | [`docs/TLF.md`](docs/TLF.md) |
| Directory/YAML realization | [`docs/DIRECTORY-PROJECTION.md`](docs/DIRECTORY-PROJECTION.md) |
| Neo4j realization | [`docs/NEO4J-PROJECTION.md`](docs/NEO4J-PROJECTION.md) |
| Normative repository contract | [`CONTRACT.md`](CONTRACT.md) |
| Representation tools | [`tools/README.md`](tools/README.md) |
| License boundary | [`LICENSING.md`](LICENSING.md) |
| Organization-wide rollout | [`Cohesian/Organization`](https://github.com/Cohesian/Organization) `KGRAPH-ROLLOUT.md` |

## Planned repository shape

```text
k-graph/
├── k-graph/           # complete Directory Projection
├── maps/              # external provider identifiers
├── cypher/            # schema and generated Neo4j expression
├── tools/             # validation, translation, and resolution
├── docs/              # detailed operational documentation
├── k-graph.toml       # data-location and URI resolver configuration
├── requirements.txt
├── CONTRACT.md
└── AGENTS.md
```

Research documents and media bodies remain in their owning repositories and
storage systems.
