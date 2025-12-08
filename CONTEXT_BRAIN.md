# THE CO-FOUNDER - CONTEXT BRAIN (v1.0 - Initialization)
*Last Updated: 2025-12-09*

---
## THE BRIDGE (SUMMARY)
**MISSION:** "The Co-Founder" (App B)
**PREVIOUS STATE:** v1-foundation (Generic Agent Architecture)
**CURRENT STATUS:** **INITIALIZATION & REBRANDING**
**OBJECTIVE:** Pivot the infrastructure from a "Coding Agency" to a "Knowledge Engine." This agent will not write code; it will ingest user brain dumps, structure them into Markdown (Vision, Roadmap), and generate briefs for the Coding Agent.

---
## 1. CURRENT GROUND TRUTH (THE NOW)

### Live Infrastructure
| Service | URL / Endpoint | Status |
|---|---|---|
| **Frontend** | `https://co-founder-frontend-534939227554.australia-southeast1.run.app` | **PENDING DEPLOY** |
| **Backend** | `https://co-founder-backend-534939227554.australia-southeast1.run.app` | **PENDING DEPLOY** |

### Architecture: The Knowledge Engine
*   **Brain:** Gemini 2.5 Pro (Supervisor) + Gemini 2.5 Flash (Scribes).
*   **Memory:** Firestore (Chat History) + GCS (The "Vault" - Markdown Files).
*   **Topology:** Supervisor -> Head of Product (Scribe) -> End.

---
## 2. THE PRIME DIRECTIVES
1.  **NO CODING:** This agent must never attempt to write `.tsx` or `.py` files unless explicitly asked to document them. Its output is **Markdown**.
2.  **THE TRUTH IS IN THE FILES:** The state of the project is stored in `VISION.md`, `ROADMAP.md`, and `RULES.md` in Cloud Storage.
3.  **ISOLATION:** We must strictly deploy to the `co-founder-*` service names to avoid overwriting the Vibe Coder.