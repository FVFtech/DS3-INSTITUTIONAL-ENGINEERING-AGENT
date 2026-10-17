import pytest
from ds3_agent.evolution import EvolutionBlocked, load_policy, validate_approval_record
def test_human_approval_is_mandatory():
 p=load_policy(); assert p["human_approval_required"] is True; assert p["auto_merge"] is False; assert p["auto_deploy"] is False; assert p["transaction_authority"] is False; assert p["signing_authority"] is False
def test_approval_record_needs_rationale():
 with pytest.raises(ValueError): validate_approval_record({"candidate_id":"c","reviewer":"human","decision":"rejected","reviewed_at":"now"})
def test_valid_review_record_is_metadata_only():
 validate_approval_record({"candidate_id":"c","reviewer":"reviewer-id","decision":"approved_for_separate_integration","rationale":"Reviewed candidate and evaluation","reviewed_at":"2026-10-17T12:00:00Z"})
