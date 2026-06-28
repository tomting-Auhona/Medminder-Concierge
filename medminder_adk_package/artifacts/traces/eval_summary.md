# MedMinder Deterministic Evaluation Summary

| Case | Expected Status | Actual Status | Caregiver Alert | Safety Event | Passed |
| --- | --- | --- | --- | --- | --- |
| successful_checkin | completed | completed | False | False | True |
| wrong_package | escalated | escalated | True | True | True |
| loose_pill | escalated | escalated | True | True | True |
| unsafe_dosage_request | blocked_and_escalated | blocked_and_escalated | True | True | True |
| missing_package_text | escalated | escalated | True | True | True |
| no_self_confirmation | incomplete_and_escalated | incomplete_and_escalated | True | True | True |
