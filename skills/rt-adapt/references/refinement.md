# Proposing TTP variants (decision support)

When a technique is blocked or detected mid-engagement, propose a short ranked list of variant options the operator can choose from. Order by how directly each preserves the current objective with the least new risk. You propose and rank; the human operator decides and executes.

Reason with the adversary mindset (`skills/_shared/references/adversary-mindset.md`): how the emulated actor would get past the observed control to keep pursuing the objective. That reasoning is in scope only as far as this authorized test needs it.

Rank in this order:

1. **Sibling sub-technique.** A different sub-technique under the same parent that pursues the same goal by another method (e.g. if `T1566.001` Spearphishing Attachment is blocked at the mail gateway, try `T1566.002` Spearphishing Link). Lowest conceptual change.
2. **Alternative technique for the same objective.** A different technique that reaches the same objective (e.g. another route to initial access, or another credential-access method). Use this when the whole technique is burned, not just one variant.
3. **OPSEC change to the same technique.** Keep the technique but change tradecraft to evade the observed control (timing, tooling, obfuscation, infrastructure). Use when the technique still fits but was noisy.

For each option give: the `technique_id` + `framework` (`attack` | `atlas` | `aadapt`), one line on why it may evade the observed control, and an OPSEC note. Validate every id with `validate.py` before offering it.

Two hard rules:

- **Human on the trigger.** You propose and rank; the operator decides and executes. Never act.
- **Stay grounded.** Only offer real, validated techniques. Do not invent a technique to fit the moment; if nothing good fits, say so and recommend pausing to reconsult the plan or deconflict.

Record the chosen move in the `adaptation` field of the log entry for the blocked or detected action.
