from app.naming_registry import REGISTRY

def shield_pm(vibe_manifest: dict) -> str:
    """The Dynamic Prose Firewall. Maps flat JSON to X-Ray stories for the PM."""
    m = vibe_manifest.get(REGISTRY.MANIFESTO) or {}
    
    if not m or not m.get("core_idea"):
        return "A fresh vision with no core idea locked yet. Lead the discovery."
        
    story = [f"Project: {m.get('core_idea')} for {m.get('target_user', 'its audience')}."]
    
    # The Physics Spine
    spine_keys = ['founder_frustration', 'competitor_belief', 'business_model', 'success_sentence']
    
    for key in spine_keys:
        label = key.replace('_', ' ').title()
        val = m.get(key)
        # 15 char threshold matches the physics gate in architect.py
        if val and len(str(val)) > 15:
            story.append(f"{label}: {val}")
        else:
            # The X-Ray: Force the PM to see the void
            story.append(f"{label}: [MISSING - CRITICAL GAP]")
    
    return "\n".join(story)
