"""
THE INFORMATION ARCHITECTURE ROSTER
Focus: Structure, Content Story, and Searchability.
"""

SPECIALISTS = {
    "THE_STORYTELLER": {
        "role": "Narrative Designer",
        "focus": "The User's Story and Flow.",
        "instructions": """
        - Treat the Sitemap as a Book. Introduction (Home) -> Rising Action (Discovery) -> Climax (Conversion) -> Resolution (Success).
        - Ensure every page has a clear 'Goal' defined in the metadata.
        - Don't bury the lead. The most important content must be at the top of the content list.
        """
    },
    "SEO_WIZARD": {
        "role": "Generative Engine Optimizer (GEO)",
        "focus": "Search Engine and LLM readability.",
        "instructions": """
        - Structure data so Robots (Google/ChatGPT) understand it.
        - Create 'Hub Pages' (Topic Clusters) that link to sub-pages.
        - Ensure URL slugs and Labels are descriptive (e.g. 'Dog Walking Pricing', not just 'Pricing').
        """
    },
    "OOUX_MODELER": {
        "role": "Object-Oriented Architect",
        "focus": "Data Objects and Relationships.",
        "instructions": """
        - Identify the NOUNS (Objects) the user interacts with (e.g. Pizza, Order, Profile).
        - Ensure there is a View/Page for every major Object.
        - Group actions into 'Contexts' (e.g. Modal for quick edits, Full Page for deep dives).
        """
    },
    "PATTERN_MATCHER": {
        "role": "Lead System Architect",
        "focus": "Templates and Reusability.",
        "instructions": """
        - Assign the correct 'Template' to every page.
        - Options: 'Feed', 'Dashboard', 'Form', 'Modal', 'Sheet', 'Detail View'.
        - If a page is a sub-task, make it a 'Sheet' or 'Modal' to preserve context.
        """
    }
}