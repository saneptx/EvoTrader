# ADR-0007: Arm B (fixed strategy + memory) intervention

- Status: Proposed — to be decided before Week 4

## Context
Spec §1 notes a fixed strategy may not be able to use memory operationally.

## Options under consideration
1. Memory informs a *deterministic decision policy* layered on a fixed DSL (e.g. choose among a
   pre-registered, fixed set of strategies per fold using retrieved training-only episodes).
2. Memory informs only hypothesis selection/ordering, with the strategy itself fixed.

No decision yet; the chosen policy must be preregistered and match budgets with arms A/C/D.
