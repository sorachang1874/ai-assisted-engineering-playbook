# Example: Contract Owner Matrix

This example shows how to define one shared field before implementation.

## Contract

`filter_contract.facet_count_scope`

## Owner Matrix

| Property | Value |
| --- | --- |
| Owner | Projection reader |
| Source of truth | Canonical projection facet counts |
| Allowed values | `exact_projection`, `global_full_population`, `unavailable` |
| Derivation | Derived only by projection reader from projection metadata |
| Producers | Projection writer, projection reader |
| Consumers | `/progress`, `/dashboard`, `/candidates`, `/board-patches`, UI filter panel |
| Fallback | None in normal path |
| Migration bridge | Legacy candidate page summary may be read only in migration tests |
| Deletion condition | All public endpoints pass parity preflight for 7 consecutive CI runs |
| Preflight | `make test-contract FILTER_CONTRACT=1` |

## Regression Shape

The preflight should fail if any public endpoint reports a different value for the same projection.

## Rule

Do not let endpoints independently infer facet scope from their local payload shape.

