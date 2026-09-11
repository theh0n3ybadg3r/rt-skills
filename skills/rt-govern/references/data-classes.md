# Data classes and the mixed-by-phase egress policy

Two classes. Classify the **advisory/input**, not the framework catalog.

## `public-reference`

Open-source, already-public material: published CTI, vendor blogs, ATT&CK/ATLAS reference pages, news. Nothing here is engagement- or target-specific.

- `egress_permitted.source_content: true`, the text is already public; sending excerpts to an external service is acceptable under scope.

## `engagement-sensitive`

Anything tied to a specific engagement or target: internal threat reports, scoping documents, target-derived intelligence, client-confidential material, anything under NDA or classification.

- `egress_permitted.source_content: false`, do not send the advisory's source content to any third-party service. The `validate` helper honors this fully: it runs locally and sends only public catalog requests, never source text.
- **Honest limitation (KTD5):** the extraction and verification _reasoning_ is performed by the LLM. With a hosted model (Claude Code / Codex default), that inference sends the source content to the model provider, which is itself egress. So `source_content: false` is a **hard** guarantee only with a local model or an enforced egress boundary; with a hosted model it means "no egress beyond the authorized model host," and the run must stay on that authorized boundary. Do not treat the record as proof the text never left the machine. For a truly air-gapped engagement, run a local model.

## Framework catalog fetch is always permitted (Assumption A1)

In **both** classes, `egress_permitted.public_catalog_fetch: true`. Fetching the public ATT&CK / ATLAS / AADAPT catalog to validate technique IDs carries **no** source content, only public catalog data comes back, and the `validate` helper sends nothing about the advisory. This is the load-bearing reconciliation that lets live ID validation run even on an engagement-sensitive advisory.

## When unsure

Default to `engagement-sensitive`. Over-restricting egress is safe; under-restricting is not.
