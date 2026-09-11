# ATT&CK (Enterprise) mapping

Use `framework: attack` for adversary behavior against enterprise IT/OT, endpoints, servers, cloud, identity, and network. This is the default taxonomy; use `atlas` or `aadapt` only when the target-type rule in `skills/_shared/references/framework-mapping.md` routes there (`atlas` when the AI system itself is the subject of the test, `aadapt` for payment / clearing / settlement infrastructure).

- **IDs are `T####` / `T####.###`.** Choose the sub-technique when the source names the specific method (`T1566.001` Spearphishing Attachment vs `T1566.002` Spearphishing Link); fall back to the parent (`T1566`) when it does not.
- Never record a tactic (`TA####`), mitigation (`M####`), group (`G####`), software (`S####`), or data-source (`DS####`) id as a technique. The `validate` helper refutes these as `wrong-id-type`. Extract the behavior an actor or malware performed, not the actor or malware name.
- Names must match the official ATT&CK name (the child name or the `Parent: Child` display form both validate; see `framework-mapping.md`).
