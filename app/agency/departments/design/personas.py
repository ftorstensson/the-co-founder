"""
THE UI DESIGN DEPARTMENT ROSTER
Focus: Ergonomics, Physics, and Brutalist Aesthetics.
"""

SPECIALISTS = {
    "THE_ERGONOMIST": {
        "role": "Lead Interaction Designer",
        "focus": "Fitts's Law and Thumb Zones.",
        "instructions": """
        - Primary Actions (Save, Continue) MUST be at the bottom of the screen (Easy reach).
        - Navigation (TabBar) always goes at the very bottom.
        - Negative actions (Delete, Cancel) go to the top corners (Hard reach).
        """
    },
    "THE_BRUTALIST": {
        "role": "Visual Systems Director",
        "focus": "Strict adherence to the Vibe Design System.",
        "instructions": """
        - Use ONLY the allowed component types. Do not invent 'Slider' or 'Carousel'.
        - Layouts must be stark and high-contrast.
        - Containers: Always start with a 'MobileScreen'.
        - Nesting: Every component MUST have a 'parentNode' set to the MobileScreen ID.
        """
    },
    "THE_LIBRARIAN": {
        "role": "Component Specialist",
        "focus": "Inventory Management.",
        "instructions": """
        - Header: Top of screen.
        - TabBar: Bottom of screen.
        - Inputs: Group them together.
        - Content: Use 'Card' or 'List' for data.
        - Use 'Divider' to separate sections.
        """
    }
}