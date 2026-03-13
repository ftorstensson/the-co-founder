from app.naming_registry import REGISTRY

def safe_state_merge(project_id, scribe_output, db):
    # Reject any attempt to touch ZONE A
    if REGISTRY.ENVELOPE in scribe_output or REGISTRY.MANIFESTO in scribe_output:
        raise ValueError("SCRIBE VETO: Attempted to overwrite Immutable Envelope.")

    # Firestore Path Merge
    update_payload = {f"{REGISTRY.STATE}.{k}": v for k, v in scribe_output.items()}
    db.collection("cofounder_boards").document(project_id).update(update_payload)
