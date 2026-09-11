# Threat Advisory: TA-2026-014 Intrusion Set "Dusk Harrier"

## Initial Access

On 2026-05-02 the actor sent a phishing email carrying a malicious .docx attachment to three
finance-team users. When opened, the attachment executed a macro that downloaded a second-stage loader.

## Credential Access

Following execution, the operator dumped credentials from LSASS memory on the initial host using a
renamed copy of a well-known dumping utility.

## Notes

Public reporting only. No client-specific data in this advisory.
