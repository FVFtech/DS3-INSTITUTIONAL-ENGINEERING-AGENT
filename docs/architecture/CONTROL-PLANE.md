# Institutional Engineering Agent — controlled planning

This implementation provides persistent task records, an LLM proposal adapter, an allowlisted
read-only tool layer, review-state transitions, and event history. It is **not** an
autonomous code-writing/deployment system, an authenticated multiuser approval service,
or a settlement control system.

## Design
```text
Operator CLI -> SQLite task state -> deterministic read-only source retrieval
                                   -> LLM JSON proposal -> schema validation
                                                      -> awaiting_approval
Human operator (local opt-in) -> review metadata -> approved/rejected
                                (NO code apply, signing, deployment or merge)
```

## Configuration
Requires Python 3.11+. Install `pip install -e ".[dev]"`. Provide
`DS3_LLM_API_KEY` in a trusted, secret-managed environment. Optional
`DS3_LLM_MODEL` selects model, `DS3_LLM_ENDPOINT` configures a compatible
HTTPS chat-completions endpoint, and `DS3_TASK_DB` selects the SQLite path.
Do not commit the database or API credentials.

```sh
ds3-agent task-create "Review reconciliation failure handling"
ds3-agent task-list
ds3-agent task-run TASK_ID
ds3-agent task-show TASK_ID
# For local trusted demonstrations only; operator identity is not authenticated:
DS3_ALLOW_LOCAL_REVIEW=1 ds3-agent task-review TASK_ID reviewer@example.org approved "Reviewed proposal"
```

The model receives the task text and approved source-registry metadata. It cannot call
shell, filesystem-write, GitHub mutation, financial APIs, or transaction execution tools.
The fixed `read_project_file` tool supports three allowlisted documentation files; it
is not exposed to the model in this version. Providers are trusted to process their
inputs under the applicable contracts; avoid personal/financial secrets in task text.

## Security limitations and next steps
* SQLite is persistent on a single host, not high availability. Use PostgreSQL,
  queue leases, retries and idempotency before multi-worker production usage.
* The local CLI review flag is a demonstration barrier, not authentication.
  Integrate SSO/OIDC, enforced reviewer roles, two-person reviews for material
  changes, and tamper-evident externally shipped audit logs before institutional use.
* Audit events are append-only by application convention but are mutable by a
  database administrator. They do not prove independent audit integrity.
* LLM output is untrusted. JSON schema validation is structural, not proof of
  security or correctness; human review and CI are mandatory for proposed changes.
* Approving a task **does not authorize execution** and no code-changing,
  payment, signing, auto-merge, or production deployment capability exists.
* HTTP endpoint URL should be configured only by trusted operators; limit
  outbound egress and provider choices in a production deployment.
* Do not store sensitive instructions, customer data, secrets or PII in SQLite prompts.
* This release processes tasks synchronously; there is no daemon scheduler.
