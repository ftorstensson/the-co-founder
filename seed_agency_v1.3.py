import os
from google.cloud import firestore

db = firestore.Client(project=os.environ.get('GCP_PROJECT', 'vibe-agent-final'))

def seed():
    print("🧹 Purging old roster and registry...")
    [d.reference.delete() for d in db.collection('agency_roster').stream()]
    [d.reference.delete() for d in db.collection('department_registry').stream()]

    # 1. THE DEPARTMENTS
    depts = {
        'BIG_IDEA_TEAM': 'THE BIG IDEA',
        'OPPORTUNITY_TEAM': 'THE OPPORTUNITY',
        'PEOPLE_TEAM': 'THE PEOPLE',
        'EXPERIENCE_TEAM': 'THE EXPERIENCE',
        'MVP_TEAM': 'THE MVP'
    }
    
    for i, (k, v) in enumerate(depts.items()):
        db.collection('department_registry').document(k).set({
            'id': k,
            'label': v,
            'dept_index': i
        })
        print(f"✅ Created Dept: {v}")

    # 2. THE GLOBAL HUB
    global_agents = [
        {'id': 'master_pm', 'name': 'Project Manager', 'role': 'Lead Co-Founder', 'tier': 'FLASH'},
        {'id': 'global_editor', 'name': 'Editor-in-Chief', 'role': 'The Shield', 'tier': 'PRO'}
    ]
    for agent in global_agents:
        db.collection('agency_roster').document(agent['id']).set({
            'id': agent['id'],
            'display_name': agent['name'],
            'dept_id': 'HUB',
            'role_index': 0,
            'model_tier': agent['tier'],
            'layer_id': 'GLOBAL',
            'system_prompt': f"You are the {agent['name']}. {agent['role']}."
        })

    # 3. THE STRIKE TEAMS (5 Agents per Paper)
    roster = {
        'BIG_IDEA_TEAM': ['Visionary Architect', 'Commercial Lead', 'Product Realist', 'Synthesizer', 'Editor-in-Chief'],
        'OPPORTUNITY_TEAM': ['Market Analyst', 'Competitive Intelligence Lead', 'Opportunity Mapper', 'Synthesizer', 'Editor-in-Chief'],
        'PEOPLE_TEAM': ['Audience Strategist', 'Psychographic Analyst', 'Tipping Point Strategist', 'Synthesizer', 'Editor-in-Chief'],
        'EXPERIENCE_TEAM': ['Convention Researcher', 'Engagement Mechanic Specialist', 'Social Proof Architect', 'Synthesizer', 'Editor-in-Chief'],
        'MVP_TEAM': ['Scope Architect', 'Cut List Enforcer', 'Validation Strategist', 'Synthesizer', 'Editor-in-Chief']
    }

    for d_id, agents in roster.items():
        dept_slug = d_id.lower().replace('_team', '')
        for i, name in enumerate(agents):
            agent_slug = name.lower().replace(' ', '_').replace('-', '_')
            agent_id = f"strat_{dept_slug}_{agent_slug}"
            db.collection('agency_roster').document(agent_id).set({
                'id': agent_id,
                'display_name': name,
                'dept_id': d_id,
                'role_index': i,
                'model_tier': 'PRO',
                'layer_id': 'STRATEGY',
                'system_prompt': f"You are the {name}."
            })
            print(f"   👤 Hired: {name} ({d_id})")

    print("\n🎉 MISSION V1.3 RESURRECTED. Roster is synchronized.")

if __name__ == "__main__":
    seed()