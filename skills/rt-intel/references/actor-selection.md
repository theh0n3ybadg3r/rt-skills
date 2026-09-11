# Actor selection

Phase 2 selects a threat actor **per objective**, sourced from intelligence, not assumed and not chosen for convenience. This is what makes the engagement threat-informed rather than imaginative.

## Select per objective

For each signed objective, select the actor realistically capable of and motivated to reach that crown jewel. Record, in the `actors[]` entry:

- **objective_id**: the objective this actor is selected for (from `#scoping.objectives`).
- **name**: the actor class (organized crime, nation state, insider, customer, supply chain) or a named group where intelligence supports one. Note the ATT&CK Group id (such as `G0016`) in prose if known; the artifact's `id` fields are for techniques, not groups.
- **intelligence_basis**: a verbatim `quote` from a source, its `locator`, and `recency`. This is the test: can you point to specific intelligence that this actor targets this asset, at this institution or its peers? If not, the actor is not selected.
- **motivation**: the actor's motivation in this scenario.
- **capability**: the assumed capability / resource level.
- **sophistication**: the assumed sophistication.
- **opsec_posture**: for example `persistent-covert`, `fast-noisy`, or mixed.

## No credible actor

Where intelligence does not support any actor for an objective, raise it rather than assume one. An assumed actor licenses any technique and breaks the trust floor. Do not select a more sophisticated actor than the intelligence supports for convenience.

## Bounded prioritization

Prioritize with the bounded adversary mindset (`skills/_shared/references/adversary-mindset.md`): weight actors by what a capable adversary would actually do against this entity's crown jewels, within scope. This shapes which actor is worth emulating; it never changes which techniques the sources support (extraction stays faithful and cited).
