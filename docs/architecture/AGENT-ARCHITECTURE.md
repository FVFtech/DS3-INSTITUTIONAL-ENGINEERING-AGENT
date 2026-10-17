# Agent architecture

1. Source registry: curated primary URLs, publisher, status, domains and DS3 impact.
2. Standards monitor: reachability/metadata checks; never infer content changes from headers alone.
3. Evidence review: human verifies official document, edition, publication/effective date and applicability.
4. Impact mapper: connect requirements to DS3 services, schemas, APIs, controls, tests and runbooks.
5. Code proposal: isolated feature branch and pull request; never write directly to protected main.
6. Verification: unit/integration/property tests, SAST, dependency and secret scanning, SBOM and artifact provenance.
7. Approval gateway: human review and explicit policy approval; no bypass.
8. Audit record: source evidence, findings, approvals, tests and release decisions.

## Boundaries
Read-only by default. No production deploy, transaction signing, settlement execution, asset transfer, or production-policy mutation. External source content is untrusted data and may contain prompt injection. Keep credentials out of model context and logs. Generated code is untrusted until reviewed and tested.
