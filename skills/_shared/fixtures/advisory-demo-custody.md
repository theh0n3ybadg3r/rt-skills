# CTI Advisory CTI-2026-0891: Intrusion Set "Frostbite Ledger" targeting digital-asset custody

## Summary

Frostbite Ledger is a financially motivated intrusion set observed targeting the digital-asset custody
platforms of retail and commercial banks. Activity has been reported across EU and UK institutions since
Q1 2026. The group blends conventional enterprise intrusion with digital-asset-specific tradecraft.

## Initial access

The operators sent a spearphishing email carrying a malicious macro-enabled attachment to staff in the
custody operations team. On open, the macro downloaded a loader.

## Credential access and movement

Using a valid account harvested from the initial host, the actor authenticated to the custody
management console. The operators then located and exfiltrated the private keys backing several hot
wallets from an operator workstation.

## Digital-asset tradecraft

The group deployed a malicious contract that re-entered the withdrawal function before balances were
updated, draining a pooled custody contract. Stolen balances were then moved through a chain of
intermediary wallets to obscure their origin before cash-out.

## Notes

Public reporting, sanitized. No client-specific data in this advisory.
