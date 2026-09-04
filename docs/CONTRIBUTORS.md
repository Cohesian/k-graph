# Contributors

K accepts resources only from contributors registered in `k-graph.toml`.
Registration grants an identity in the acceptance namespace; it does not give
the contributor ownership of K topology.

The current set is:

$$
C_{\mathcal K}=\{\texttt{research}\}.
$$

Research is the active v2 owner of scientific documents, executable studies,
and study media. Studio is a production workstation, not a K contributor.
Resources it produces for Research remain addressed under `c_research` and may
record `produced_by = "studio"` in Research's inventory.

## Accepted relation

For node $v$, contributor $c$, hierarchy $H=(h_1,\ldots,h_n)$, and resource
key $p$, K stores:

$$
(\operatorname{id}(v),c,H,p)\mapsto(q,z).
$$

The contributor and hierarchy localize ownership. The resource key selects a
logical resource. The protocol $q$ defines its concrete boundary and the
canonical digest $z$ fixes the exact accepted content.

Any `T`, `L`, `E`, or `Ed` node may carry accepted resources without changing
its TLE kind or graph neighborhood.

## Responsibility boundary

| Participant | Responsibility |
|---|---|
| K | accepted address, protocol, digest, topology |
| Contributor | resource bytes, stores, locations, production provenance |
| Tether | protocol interpretation, hashing, comparison, resolution |
| Consumer | chosen replicas, layout, composition, presentation |

Contributors may retain work that is never proposed. A compatible contributor
package is not automatically admitted to K; admission and every accepted
change remain explicit.

## Contributor package

Each contributor exposes a v2 `contributor.toml` and one or more inventories.
An inventory record repeats the durable address, current rooted path, protocol,
digest, and contributor-owned locations. Tether can then compare the complete
record with K in bulk rather than issuing one call per graph node.

For example:

```bash
tether resource list ../research --hierarchy documents --key md
tether resource resolve ../research --path T-math/L-division/E-01-introduction
tether contributor check ../research
```

Exact commands and onboarding are documented in
[Tether](../../tether/docs/CONTRIBUTOR-ONBOARDING.md). Proposal mechanics are
described in [`PROPOSALS.md`](PROPOSALS.md).
