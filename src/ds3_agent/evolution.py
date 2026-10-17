"""Candidate-only DSPy/GEPA evolution scaffold. No production authority."""
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
POLICY=ROOT/"config/evolution-policy.json"
DATASET=ROOT/"data/evolution-eval.jsonl"
OUT=ROOT/"artifacts/evolution-candidates"
class EvolutionBlocked(RuntimeError): pass
def load_policy(path=POLICY):
 p=json.loads(Path(path).read_text(encoding="utf-8"))
 if p.get("human_approval_required") is not True: raise EvolutionBlocked("Human approval must remain mandatory.")
 for k in ("auto_merge","auto_deploy","transaction_authority","signing_authority","production_policy_mutation"):
  if p.get(k) is not False: raise EvolutionBlocked(f"Unsafe policy setting: {k}")
 return p
def load_examples(path=DATASET):
 path=Path(path)
 if not path.exists(): raise EvolutionBlocked("Evaluation dataset missing.")
 rows=[json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
 if any(not isinstance(r.get("task"),str) or not isinstance(r.get("expected_criteria"),list) for r in rows): raise ValueError("Every example requires task and expected_criteria[]")
 return rows
def evolve_prompt(target: str, approve: bool=False) -> Path:
 p=load_policy()
 if approve: raise EvolutionBlocked("Approval cannot be granted through the evolution command.")
 if target not in p["allowed_evolution_targets"]: raise EvolutionBlocked("Target is not allowlisted.")
 rows=load_examples()
 if len(rows)<p["minimum_eval_examples"]: raise EvolutionBlocked("Evaluation set below configured minimum.")
 try: import dspy
 except ImportError as exc: raise EvolutionBlocked('Install optional dependency: pip install -e ".[evolution]"') from exc
 if not hasattr(dspy,"GEPA"): raise EvolutionBlocked("Installed DSPy does not expose dspy.GEPA; validate and pin a compatible version.")
 candidate={"target":target,"created_at":datetime.now(timezone.utc).isoformat(),"status":"candidate_pending_human_review","optimizer":"DSPy GEPA","dataset_count":len(rows),"policy_version":p["policy_version"],"integration_status":"scaffold_only","note":"No GEPA optimization has run. Candidate is not active and does not change code or policy.","review_checklist":["Review candidate diff and prompt-injection resistance","Run held-out evaluation against baseline","Review financial correctness and security regressions","Verify no elevated tool permissions","Record human reviewer, decision, timestamp and rationale","Integrate only through a separate protected pull request"]}
 OUT.mkdir(parents=True,exist_ok=True)
 safe="".join(c if c.isalnum() or c in "-_" else "-" for c in target)
 dest=OUT/f"{safe}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
 dest.write_text(json.dumps(candidate,indent=2),encoding="utf-8")
 return dest
def validate_approval_record(record):
 required={"candidate_id","reviewer","decision","rationale","reviewed_at"}
 if required-record.keys(): raise ValueError(f"Missing approval fields: {sorted(required-record.keys())}")
 if record["decision"] not in {"approved_for_separate_integration","rejected","changes_requested"}: raise ValueError("Unsupported decision")
 if not all(isinstance(record[k],str) and record[k].strip() for k in required): raise ValueError("Approval fields must be non-empty strings")
