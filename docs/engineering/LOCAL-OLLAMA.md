# Free local LLM for DS3 Agent (macOS)

Install Ollama from https://ollama.com/download/mac and start the Ollama app.
In Terminal:

```sh
ollama pull llama3.2:3b
ollama list
# Use the DS3 feature branch that contains this integration:
git fetch origin
git switch feature/local-ollama-llm
python -m pip install -e ".[dev]"
export DS3_LOCAL_LLM=1
export DS3_LLM_ENDPOINT=http://127.0.0.1:11434/v1/chat/completions
export DS3_LLM_MODEL=llama3.2:3b
unset DS3_LLM_API_KEY
ds3-agent task-create "Review DS3 reconciliation architecture"
ds3-agent task-list
ds3-agent task-run REPLACE_WITH_NEW_TASK_ID
ds3-agent task-show REPLACE_WITH_NEW_TASK_ID
```

Ollama must be running locally at port 11434. The local model is downloaded once;
inference uses your Mac's compute and no paid OpenAI API credits.
Model quality and speed depend on available system memory and CPU/GPU.
Use a fresh task ID because failed tasks are terminal in the current state machine.

## Security
Local HTTP is enabled only with `DS3_LOCAL_LLM=1`, to localhost/loopback
on port 11434, at the exact `/v1/chat/completions` path.
Remote endpoints still require HTTPS and an API key. Never expose Ollama to your LAN,
the public Internet, or untrusted local users. Local AI output still requires human review;
it cannot execute code, settlements, payments or deployments.
