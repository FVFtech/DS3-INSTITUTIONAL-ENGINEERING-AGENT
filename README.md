# DS3 Institutional Engineering Agent

**Security-first institutional engineering research and proposal control plane** for Digital Settlements V3 (DS3).

The repository combines standards-source monitoring with persistent, human-reviewed LLM engineering proposals. It is a development-stage control plane, **not** a production-certified settlement or autonomous coding system. It does not execute transactions, sign instructions, change repositories, merge pull requests or deploy software.

## Current capabilities

| Capability | Status |
| --- | --- |
| Curated HTTPS standards-source registry and metadata monitor | Implemented |
| Source-change review report | Implemented |
| Persistent task records and state transitions | Implemented (single-host SQLite) |
| LLM-generated, schema-validated engineering proposals | Implemented (OpenAI-compatible remote API) |
| Scoped, read-only source retrieval and file allowlist | Implemented |
| Human approval/rejection record and audit events | Implemented (local, unauthenticated demonstration) |
| Optional DSPy/GEPA self-evolution | Candidate-only scaffold; no optimizer loop |
| Local Ollama inference | Implemented on the `feature/institutional-agent-control-plane` branch; **not yet merged to main** |
| Authenticated RBAC, durable worker queue, HA persistence, autonomous PR generation | Not implemented |

> **Branch note (October 19, 2026):** PR #2 delivered the control plane to `main`. PR #3 added free local Ollama support but was merged into `feature/institutional-agent-control-plane`, not `main`. For the local setup below, switch to that feature branch until the Ollama changes are separately brought into `main`.

## Requirements and installation

- Python **3.11+**
- Git; macOS/Linux Terminal (Windows PowerShell uses a different activation command)
- For remote LLM inference: a compatible provider API key and API credits
- For free local inference: Ollama installed and a model downloaded

From the repository directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
ds3-agent --help
python -m pytest
```

When you open a new Terminal window, run `source .venv/bin/activate` again. If `ds3-agent` is not found, check `which python` and `python -m pip show ds3-institutional-engineering-agent` before reinstalling.

## Standards intelligence

```bash
ds3-agent sources
ds3-agent check-config
ds3-agent sync
ds3-agent report
```

`sync` checks source-page HTTP metadata, not the documents' legal meaning. Humans must verify editions, status, effective dates and applicability.

## Engineering proposal workflow (main branch)

Create and inspect a task:

```bash
ds3-agent task-create "Review DS3 reconciliation architecture"
ds3-agent task-list
```

Copy the generated UUID from `task-list`; **`YOUR_TASK_ID` is a placeholder** and must be replaced with the actual value.

For remote OpenAI-compatible models, configure an API key privately in your shell:

```bash
read -rs "DS3_LLM_API_KEY?Enter API key: "
echo
export DS3_LLM_API_KEY
# Optional: export DS3_LLM_MODEL=gpt-4.1-mini
ds3-agent task-run YOUR_TASK_ID
ds3-agent task-show YOUR_TASK_ID
```

API billing is separate from a ChatGPT subscription. Do not enter API keys into prompts, chat, git history or screenshots.

The task transitions from `pending` to `running`, then to `awaiting_approval` if proposal generation succeeds or `failed` if it does not. Failed tasks are terminal in this version; create a new task after resolving the cause. Approval only records a decision: it **does not apply generated changes**.

For a **trusted local demonstration only**:

```bash
DS3_ALLOW_LOCAL_REVIEW=1 ds3-agent task-review YOUR_TASK_ID reviewer@example.org approved "Reviewed proposed changes"
```

This CLI reviewer label is not independently authenticated and must not be treated as institutional authorization.

## Free local LLM with Ollama (feature branch)

To use local inference without OpenAI API credits, install Ollama from <https://ollama.com/download/mac>, start it, and download a model:

```bash
ollama pull llama3.2:3b
ollama list
```

Then use the branch containing the Ollama adapter:

```bash
git fetch origin
git switch feature/institutional-agent-control-plane
source .venv/bin/activate
python -m pip install -e ".[dev]"
export DS3_LOCAL_LLM=1
export DS3_LLM_ENDPOINT=http://127.0.0.1:11434/v1/chat/completions
export DS3_LLM_MODEL=llama3.2:3b
unset DS3_LLM_API_KEY
ds3-agent task-create "Review reconciliation error handling"
ds3-agent task-list
ds3-agent task-run YOUR_NEW_TASK_ID
```

Ollama must be running locally on port 11434 and `llama3.2:3b` must appear in `ollama list`. The adapter permits HTTP only for an explicitly enabled loopback Ollama endpoint; remote endpoints require HTTPS. Local model outputs still require human scrutiny and should not contain secrets.

For details, see [Local Ollama guide](docs/engineering/LOCAL-OLLAMA.md) **on the feature branch**. Model performance varies with Mac hardware. This integration passed GitHub CI but live inference on the developer Mac has not been verified.

## Architecture and safeguards

```text
Operator CLI
    |
    v
SQLite task record ---> read-only source registry
    |                             |
    +----------> LLM proposal <---+
                    |
             schema validation
                    |
             awaiting_approval
                    |
            human review record
          (no execution authority)
```

- Model output and external sources are untrusted.
- The LLM cannot invoke arbitrary shell commands, GitHub writes, settlement APIs or payment instructions through the current tool interface.
- No automatic repository modification, signing, transaction execution, asset transfer, production deployment, auto-merge or certification assertion.
- SQLite storage and its audit events are not tamper-evident or highly available.
- Local review uses a user-supplied label, not SSO or enforceable RBAC.
- No production secrets, HSM/MPC credentials, customer data or seed phrases belong in prompts or local task records.
- Technical ledger finality and legal finality must never be conflated.

See [Control-plane architecture](docs/architecture/CONTROL-PLANE.md), [Security threat model](docs/security/THREAT-MODEL.md), [Agent architecture](docs/architecture/AGENT-ARCHITECTURE.md) and [Change protocol](docs/engineering/CHANGE-PROTOCOL.md).

## Testing and development

```bash
python -m pytest
python -m compileall -q src tests
python -m ruff check src/ds3_agent/control_plane.py src/ds3_agent/scoped_tools.py src/ds3_agent/orchestrator.py tests/test_control_plane.py tests/test_orchestrator.py --select E4,E7,E9,F
```

GitHub Actions runs install, TOML validation, compilation, tests and targeted lint checks. A passing CI job does **not** establish regulatory compliance, production readiness, or successful live model invocation.

## Controlled self-evolution

Install the optional dependency with `python -m pip install -e ".[evolution]"` and see [Self-evolution architecture](docs/architecture/SELF-EVOLUTION.md). `ds3-agent evolve code-review-instructions` creates candidate metadata only. This version does not execute a full GEPA optimization loop, apply candidates or bypass human review.

## Roadmap

1. Add authenticated operator identities and RBAC approval policies.
2. Replace local SQLite with production-grade PostgreSQL, durable jobs, idempotency and audit retention.
3. Add hardened, separately reviewed repository connectors and test-gated PR proposals.
4. Run realistic offline evaluations and prompt-injection/security regression tests.
5. Create an isolated staging deployment with budgets, network egress controls, observability and incident procedures.

## License

See [LICENSE](LICENSE).
