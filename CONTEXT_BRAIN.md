# PROJECT BRAIN: THE CO-FOUNDER (APP B)
*Current Status: V1 LIVE (Auto-Pilot Active)*

## 1. THE MISSION
We are building **"The Co-Founder"** (App B).
It is a "Knowledge Engine" designed to prevent **Context Decay** in long-running AI projects.
*   **Input:** Brain Dumps, Rants, Conversations.
*   **Process:** Background "Scribe" Agent extracts Vision, Roadmap, and Artifacts.
*   **Output:** A structured, persistent "Project Board" (Sidebar/Right Panel).

## 2. THE ARCHITECTURE (ROBUST V1)
*   **Backend:** FastAPI + LangGraph.
    *   **Brain:** `gemini-2.5-pro` (Chat), `gemini-2.5-flash` (Scribe).
    *   **Persistence:** Custom Firestore Saver (Bare Metal).
    *   **Auto-Pilot:** Uses `BackgroundTasks` to update the board after every turn.
*   **Frontend:** Next.js (React).
    *   **Data Strategy:** **Server-Side Proxy.** The UI polls the Backend (`GET /agent/projects`), avoiding fragile Client-Side DB connections.
    *   **Workspace:** Supports Pinning, Renaming, and Soft Deleting projects.

## 3. ACTIVE FEATURES
*   [x] **Split-Screen Interface:** Chat (Left) + Knowledge Base (Right).
*   [x] **Auto-Save:** Threads are saved instantly on the first message.
*   [x] **Auto-Update:** The "Scribe" updates the Right Panel in the background (~5s lag).
*   [x] **Workspace Management:** Rename, Pin, Delete projects via Context Menu.
*   [x] **Robust Deployment:** Automated Build Args for Cloud Run visibility.

## 4. NEXT IMMEDIATE GOALS
1.  **Context Injection:** Allow The Co-Founder to "Inject" the structured context back into the prompt for the *next* agent (The Vibe Coder).
2.  **Streaming:** Add token streaming for a smoother chat feel.
3.  **Artifacts:** Allow the user to download the `VISION.md` or `ROADMAP.md` as actual files.

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