# Proposals

A proposal is an asynchronous request from a registered contributor to change
K.

```text
prepared → submitted → validating → accepted | rejected
```

Only an accepted proposal changes the graph. Rejection leaves K unchanged and
does not invalidate work retained by the contributor.

## Shape

A proposal identifies:

```text
contributor
base_revision
requested_changes
resource_acceptances (optional)
rationale
```

Requested changes may:

- create nodes, relationships, or resource declarations;
- replace the editable description of a known element;
- patch named properties or relationships; or
- delete explicitly named graph elements.

Read queries help prepare and review a proposal but do not mutate K.

## PUT and PATCH

PUT replaces the complete editable description of a known node or
relationship. PATCH changes only named fields or relationships.

For example, a proposal may add `n4` and `n5`, group `n4` under existing `n3`,
and connect `n4` to `n5`. The new `GROUPS` relationship changes the graph
around `n3`; it does not become intrinsic data inside `n3`.

Moving a node changes its rooted path and may change every descendant path.
The affected node ids remain fixed, and an accepted move can expose
`(id, old_path, new_path)` changes to contributors.

Deletion must state what happens to incident relationships, descendants,
resource declarations, and accepted content references. There is no implicit
cascade.

## Atomic acceptance

K evaluates all requested changes together:

```text
accepted graph + proposal → candidate graph → validation
```

The proposal is accepted as one change only when the candidate graph preserves
the contract. Otherwise none of its requested changes are applied.

Validation covers:

- registered contributor identity;
- proposal schema and base revision;
- TLF kinds and intrinsic node properties;
- grouping reachability, acyclicity, and sibling order;
- incoming and outgoing `NEXT` degree;
- relationship targets;
- registered contributor ids and typed resource hierarchies;
- resource-key uniqueness and versioned protocols;
- protocol-derived SHA-256 agreement; and
- later, licensing and policy checks.

Review and application are manual today. This document defines the boundary
that a future automated pipeline may implement; it does not claim that the
pipeline or a submission CLI already exists.
