# Verbatim-citation contract

The trust floor for the Threat Profile Brief: no verbatim quote, no claim. Every actor selection and every technique mapping is grounded in a quote copied exactly from a source, not a paraphrase and not a creative mapping.

## What a citation must be

- **Verbatim.** The `quote` is a substring of a cited source, character for character. If you cannot find such a quote, do not record the mapping or the actor.
- **Behavior, not label.** Quote the described adversary behavior (what was done), not just a named tool. A tool name alone is not a technique; the behavior it performed is.
- **Located.** Record a `locator`: the source identifier plus section / page / line. Converting binary sources to markdown first (see the Procedure) keeps page locators stable.

## Discipline

- **One claim, one quote (at least).** A technique carries at least one `citations` entry; an actor carries an `intelligence_basis.quote`.
- **Do not over-map.** Ambiguous phrasing that could be several techniques: record the best-supported one, or none. `rt-verify` refutes a mapping whose quote does not support it.
- **Mark inference.** A mapping proposed from the actor's tradecraft rather than a described behavior sets `sourced: "inference"` and is never presented as authoritative.
- **Dedupe** repeated mentions of the same id into one entry, keeping all quotes.
- **Name accuracy matters.** Use the official technique name (the child name or the `Parent: Child` display form both validate). A wrong name is refuted by the `validate` helper.
