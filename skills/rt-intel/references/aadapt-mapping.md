# AADAPT mapping

Use `framework: aadapt` when the target is payment / clearing / settlement or digital-asset technology (cryptocurrency, blockchain, smart contracts, exchanges, custody, payment rails). This is the target-type rule in `skills/_shared/references/framework-mapping.md`; apply it by target, not by whatever a source happens to cite.

- **IDs are `ADT####` / `ADT####.###`.** Tactics are `TA####` (reused from ATT&CK) or `ADTA0001` (Fraud, the one native tactic); neither is a technique id, and the `validate` helper refutes them as `wrong-id-type`. Two AADAPT techniques adapt ATT&CK (`ADT1195` from `T1195`, `ADT1552` from `T1552`) but keep the `ADT` prefix; the `ADT30xx` range is digital-asset-native.
- Names must match the official AADAPT technique name.

## ID lookup aid

A quick reference to a few frequently cited ids (the catalog is authoritative; validate against it):

- Smart-contract exploitation: reentrancy `ADT3012.005`, oracle manipulation `ADT3012.004`, evil contract `ADT3012.002`, signature replay `ADT3012.006`.
- Consensus and chain: chain reorganization `ADT3003`, long-range attack `ADT3003.001`, eclipse attack `ADT3006`, double-spending `ADT3007.002`.
- Fund movement and laundering: siphon funds `ADT3028`, peel chains `ADT3028.005`, anonymizing services `ADT3030`.
- Market manipulation: pump and dump `ADT3021.001`, wash trading `ADT3021.003`.
- Key and credential compromise: private keys `ADT1552.004`, aggregate private-key-generation data `ADT3002`.
- Supply chain `ADT1195`, flash loans `ADT3015`, counterfeit tokens `ADT3016`.
