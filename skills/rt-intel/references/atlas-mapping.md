# ATLAS mapping

Use `framework: atlas` when the AI/ML system itself is the subject of the test: the model, its data, its pipeline, and the application wrapped around it. This is the target-type rule in `skills/_shared/references/framework-mapping.md`; apply it by target, not by whatever a source happens to cite. A single advisory about an AI product can yield both ATLAS entries (the ML-specific behavior) and ATT&CK entries (the surrounding enterprise behavior); record each under its correct framework.

- **IDs are `AML.T####` / `AML.T####.###`.** Tactics (`AML.TA####`), case studies (`AML.CS####`), and mitigations (`AML.M####`) are not technique ids; the `validate` helper refutes them as `wrong-id-type`.
- Names must match the official ATLAS technique name.
