# k-graph documentation

| Document | Purpose |
|---|---|
| [`TLF.md`](TLF.md) | Representation-independent mathematical model |
| [`DIRECTORY-PROJECTION.md`](DIRECTORY-PROJECTION.md) | Complete Git-friendly graph expression |
| [`NEO4J-PROJECTION.md`](NEO4J-PROJECTION.md) | Neo4j labels, relationships, constraints, and queries |
| [`CONTRIBUTORS.md`](CONTRIBUTORS.md) | Contributor set, node relation, formats, and boundary |
| [`RESOURCE-OVERLAY.md`](RESOURCE-OVERLAY.md) | Logical resources, identity, stores, and Tether bridge |
| [`RESOURCE-CONTRACT-V2.md`](RESOURCE-CONTRACT-V2.md) | Frozen migration target: hierarchical resource keys, protocols, and digests |
| [`PROPOSALS.md`](PROPOSALS.md) | Asynchronous graph-change requests and acceptance |
| [`ROADMAP.md`](ROADMAP.md) | Pending K query, remote-store, and Website integration work |

The normative repository boundary is [`../CONTRACT.md`](../CONTRACT.md).
The current graph files still implement resource protocol v1. The v2 contract
is normative for migration work but does not become the active persistence
contract until those files and validators are migrated.
