# STRIDE Threat Model

| Risk | MedMinder Example | Mitigation |
|---|---|---|
| Spoofing | Fake caregiver or user identity | Future authentication required |
| Tampering | Changed medication schedule | Stored schedule and audit logs |
| Repudiation | User denies check-in | Store self-confirmation history only |
| Information disclosure | Patient data leakage | PII redaction and mock data |
| Denial of service | Repeated unsafe requests | Security screen and escalation |
| Elevation of privilege | Prompt injection | Prompt-injection blocking and tool allowlist |
