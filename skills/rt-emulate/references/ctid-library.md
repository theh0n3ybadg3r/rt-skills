# Optional aid: building the selected actor's tradecraft into a path

The threat actor is selected in Phase 2 (`rt-intel`) from intelligence and recorded per objective in `#threat-profile`. Phase 3 does not choose the actor. This reference is an **optional aid** for turning that already-selected actor's documented tradecraft into a concrete attack path when the threat profile is thin on step-level detail. It never overrides the profile's actor selection or its cited techniques.

Use these public, threat-informed sources to flesh out how the assigned actor actually operates:

- **MITRE ATT&CK Groups** (`G####`): the group's associated techniques and software give a documented TTP set to draw path steps from, so a step stays faithful to what the actor has really done.
- **MITRE CTID Adversary Emulation Library**: ready-made, step-level plans for named adversaries (for example APT29, FIN7, Carbanak, Sandworm, Turla, Wizard Spider, FIN6, OceanLotus, menuPass, OilRig, Blind Eagle, and the Micro Emulation Plans for compound behaviors). Each provides an ordered operational flow and TTP-level detail with ATT&CK ids.

When you use either:

- Keep the actor and the techniques anchored to `#threat-profile`. A step drawn from one of these sources that is not in the profile is an off-profile step and must be justified from the actor's documented tradecraft, then validated.
- Adapt to this engagement's objectives and crown jewels rather than copying a public plan wholesale. The tradecraft is the source; the objectives and crown jewels are the target.
- Every technique still validates against the `validate` helper before it enters a path.
