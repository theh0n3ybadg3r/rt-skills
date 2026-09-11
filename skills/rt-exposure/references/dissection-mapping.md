# Dissection and technique mapping

Goal: a faithful, cited dissection of the vulnerability the sources actually describe, and a technique map of how it is exploited. This is analysis of what the advisory says, not a creative exercise.

## How to read the sources

- Read the advisory, CVE record, and any vendor writeup directly and fully before dissecting. Capture quotes verbatim from the source text.
- Separate the weakness (the flaw class) from the exploitation (what an attacker does with it). The dissection records both.

## What to capture

### Weakness (`weaknesses[]`)

- **cwe** and **name**: the weakness class, e.g. `CWE-89` SQL Injection, `CWE-502` Deserialization of Untrusted Data. Prefer the most specific CWE the source supports.
- **quote** + **locator**: a verbatim clause that names or describes the weakness, and where it appears.
- CWE ids are recorded for the reader but are not catalog-checked by the helper (there is no CWE catalog). The fidelity verifier judges the CWE against the quote, so the quote must genuinely describe that weakness.

### Affected surface (`affected_surface[]`)

- **component**: the affected product, component, and version range, exactly as stated.
- **quote** + **locator**: the verbatim statement of what is affected. Version numbers must come from the source, not memory.

### Exploitation techniques (`techniques[]`)

- **framework**: `attack` for enterprise IT/OT exploitation behavior, `atlas` for attacks on AI/ML systems (e.g. prompt injection, model extraction), `aadapt` for digital-asset / payment / smart-contract behavior (e.g. reentrancy, oracle manipulation). One vulnerability can yield several. See the shared framework rules in `skills/_shared/references/framework-mapping.md`.
- **id** and **name**: the specific technique. Prefer a sub-technique when the source is specific enough (e.g. an exploit against a public-facing app -> `T1190` Exploit Public-Facing Application). Map the behavior the exploitation involves, not a tool name.
- **quote** + **locator**: a verbatim sentence that grounds the mapping.

### Severity signals (`severity_signals[]`)

- **kind**: `cvss`, `epss`, `kev`, `vendor-severity`, or `exploit-availability`.
- **value**: the stated figure or status, e.g. CVSS `9.8`, EPSS `0.72`, KEV `listed`, vendor `CRITICAL`, exploit `public PoC available`.
- **quote** + **locator**: the verbatim statement. A severity number, a KEV listing, or "exploited in the wild" that is not stated in a source is invented; do not record it. The fidelity verifier refutes an ungrounded severity signal.

## Discipline

- **One claim, one quote (at least).** No verbatim quote, no claim. This holds for weaknesses, surface, techniques, and severity alike.
- **Do not over-map.** Ambiguous phrasing that could be several techniques -> record the best-supported one, or none. The dissection-fidelity verifier refutes a mapping whose quote does not support it.
- **Dedupe** repeated mentions of the same technique id into one entry keeping all quotes.
- **Name accuracy matters.** Use the official technique name; a wrong name is refuted by the `validate` helper.
