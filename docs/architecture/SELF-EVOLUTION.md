# Controlled self-evolution with DSPy and GEPA

## Objective
Use DSPy/GEPA to propose improvements to selected agent prompts and task strategies from curated, versioned evaluation data. Evolution creates candidates only; it never independently changes DS3 production behavior.

## Workflow
1. Collect reviewed failure cases and accepted examples with provenance.
2. Remove secrets, personal data, customer data and production transaction data.
3. Run optimization in an isolated environment with no write-capable GitHub token, deployment credentials, RPC credentials, signing access or production data.
4. Compare baseline and candidate on training and held-out evaluations, including financial invariants, security regressions and prompt-injection tests.
5. Generate candidate diff, scorecard, dataset version/hash, optimizer configuration and run metadata.
6. Require explicit human acceptance or rejection.
7. If accepted, integrate through a separate protected PR, CI and required code-owner reviews.
8. Re-run full regression tests before release; retain rollback to the last approved version.

## Hard boundaries
- Human acceptance and approval are always mandatory.
- Auto-merge, auto-deploy, transaction authority, signing authority and production-policy mutation are prohibited.
- Safety, authorization and refusal tests are hard gates, not weighted preferences.
- Protected targets: settlement authorization, signing policy, ledger finality, collateral eligibility, access control and production deployment.
- GEPA scores are not proof of correctness, compliance, security or financial soundness.
- Pin DSPy, optimizer configuration, model identifier, prompt version and dataset hash.

## Current implementation status
This repository includes an optional DSPy dependency, policy checks and a candidate-only scaffold. It intentionally does not execute GEPA optimization yet. Implement and test a version-pinned DSPy module, metric, expert-reviewed rubric, held-out benchmark and candidate-diff generation before enabling optimization.
