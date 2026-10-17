# Initial threat model

**Assets:** source/IP, signing policy, HSM/MPC boundary, participant credentials, settlement instructions, ledger events, collateral records, CI credentials and production configuration.

**Threats and controls**
- Prompt injection in manuals/issues/code: treat retrieved content as data; tool allowlists and narrow permissions.
- Secret exfiltration: no keys or production data in prompts/logs; secret scanning and short-lived least-privilege credentials.
- Unsafe generated patches: isolated branch, deterministic tests, static analysis, dependency/license review and human approval.
- Supply-chain compromise: locked dependencies, pinned reviewed CI actions, SBOM and artifact provenance.
- Unauthorized signing or settlement: separate proposal from authorization; quorum/limits, HSM/MPC, replay protection and idempotency.
- Duplicate/reordered ledger events: finality-aware state machine, idempotent consumers, reconciliation and exception queues.
- False compliance claims: capture status/effective date and obtain legal/compliance review.
- Cross-chain failures: model each chain's trust/finality assumptions; do not assume atomicity.
- Audit tampering: append-only records, separation of duties and integrity checks.

This document is not a penetration test, certification, or production security assessment.
