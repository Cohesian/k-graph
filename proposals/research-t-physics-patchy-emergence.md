# Research proposal: patchy-particle emergence

Status: **accepted**

## Envelope

- Contributor: `research`
- Base revision: `b89031b`
- Requested change: create one Physics subgraph and register its accepted resources
- Content references: Research's matching additive branch
- Rationale: preserve a theoretical and executable study of how local patchy-particle rules produce measurable collective structure

## Requested topology

```text
K
└── T-physics
    └── L-emergence
        └── L-patchy-particle-emergence
            ├── F-00-purpose-and-boundary
            ├── F-01-microscopic-model
            ├── F-02-local-rules-and-parameters
            ├── F-03-macroscopic-observables
            ├── F-04-experimental-laboratory
            └── F-05-findings-and-limitations
```

The six File nodes form one `NEXT` chain in their displayed order. No related
edges are requested.

## Canonical identities

| Rooted path | UUID |
|---|---|
| `T-physics` | `d46fb5c1-449d-4561-a399-93d8ec8b543f` |
| `T-physics/L-emergence` | `1bdc520d-6211-4371-8ff0-2e7b3041aea4` |
| `T-physics/L-emergence/L-patchy-particle-emergence` | `04475552-1433-4e6d-92f9-a44406c7ed18` |
| `T-physics/L-emergence/L-patchy-particle-emergence/F-00-purpose-and-boundary` | `440e4d3d-ea9f-4915-97e6-2b6b7c09c6c4` |
| `T-physics/L-emergence/L-patchy-particle-emergence/F-01-microscopic-model` | `579fa81e-4a5a-4521-98d9-ea8b69a48e8d` |
| `T-physics/L-emergence/L-patchy-particle-emergence/F-02-local-rules-and-parameters` | `65cecd50-0570-42ca-bf41-6b5ad967a0cf` |
| `T-physics/L-emergence/L-patchy-particle-emergence/F-03-macroscopic-observables` | `d01f2da8-c079-4665-b0cf-cd78f5c9727e` |
| `T-physics/L-emergence/L-patchy-particle-emergence/F-04-experimental-laboratory` | `6281d965-093e-4aaa-9ce0-2f67b95c8bbc` |
| `T-physics/L-emergence/L-patchy-particle-emergence/F-05-findings-and-limitations` | `508419e1-a1ea-4863-82b7-3636e39e5ee4` |

## Resource overlay

Every File provides the `r_md` resource under
`c_research/h_documents`. The Experimental Laboratory's Markdown resource
uses `markdown-bundle@1`, so its referenced figures are part of the same
accepted boundary. That node also provides:

- `c_research/h_documents/r_ipynb`;
- `c_research/h_code/r_hoomd`; and
- `c_research/h_media/r_emergence-video`.

Every accepted resource carries its protocol-derived SHA-256 in the node
declaration.

Store locations are deliberately absent. Research owns persistence and maps
these canonical selectors through its contributor inventory.

## Acceptance checks

- all nine UUIDs are unique;
- the grouping projection remains rooted, ordered, and acyclic;
- the File chain has reciprocal `prev` and `next` declarations;
- every declared contributor, hierarchy, resource key, protocol, and digest
  is valid;
- Directory and generated Neo4j projections are equivalent; and
- Research uses these same UUIDs and rooted paths in its route maps.
