# Future User Spaces — Forward Notes

Concepts that don't belong to any current user space but should be considered when the scope expands.
These are **not tasks** — they are design seeds. Revisit when the relevant need becomes concrete.

---

## EXPLORATION / INTERACTIVE / PLAYGROUND (name TBD)

**Trigger:** when adding maps, interactive visualisations, or other ad-hoc exploratory analysis types.

**Concept:** A space where the user explores data freely — not bound to a predefined manifest. Lower audit burden than HOME (exploration is not a reproducible publication workflow). Could host:
- Interactive maps (geographic data)
- Free-form interactive plots (brush, zoom, filter on the fly)
- "What if" comparisons outside a manifest
- Any analysis type where the user is discovering, not reproducing

**Key distinction from HOME:** HOME runs a predefined recipe and documents every step for reproducibility. EXPLORATION lets the user poke at data without that contract. They are parallel, not competing — a user might explore first, then formalise a finding into a BLUEPRINT manifest that runs in HOME.

**Design note:** This space can live alongside HOME, BLUEPRINT, TEST_LAB, GALLERY as a fifth (or sixth) user space. It does not need to fit inside any existing space.

**When to revisit:** when maps or interactive plot types are scoped for implementation.
