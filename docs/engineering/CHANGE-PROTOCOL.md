# DS3 change protocol

Every change touching cash, securities, collateral, settlement, signing, ledger, reconciliation or legal evidence must document:

1. Affected services, APIs, schemas, migrations and runbooks.
2. Official source URL, identifier, revision, publication/effective date, status and reviewer.
3. Invariants: double-entry integrity, balance conservation, authorization, limits, idempotency, ordering and recovery.
4. Technical finality separately from legal finality; chain-specific finality policy.
5. Unit, negative, integration, replay/duplicate, timeout/partial-failure and reconciliation tests as applicable.
6. Threat-model delta, dependency review, static analysis and secret scan.
7. Staging, monitoring, rollback, operator runbook and explicit approver.
8. No unsupported claim of live connectivity, bank acceptance, certification, eligibility or readiness.

Block merge when required evidence or critical tests are missing. Never skip tests to green a pipeline.
