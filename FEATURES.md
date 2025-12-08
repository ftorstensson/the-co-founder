# VIBE CODER - FEATURE LEDGER
*The definitive list of protected features. Do not modify these without explicit verification.*

## 1. Core Infrastructure (The Bedrock)
- [x] **Hybrid Brain:** Backend uses `gemini-2.5-pro` for Supervisor/PM and `gemini-2.5-flash` for Workers.
- [x] **Gemini Protocol Adapter:** Backend wraps ToolMessages in HumanMessages to prevent 500 Errors with Vertex AI.
- [x] **Memory Persistence:** Custom `CustomFirestoreSaver` uses time-sortable IDs to ensure conversation history is never lost (Amnesia Fix).
- [x] **Cloud Storage Workspace:** Agent writes user code to Google Cloud Storage (`gs://vibe-agent-user-projects`) via the `write_file` tool.

## 2. Frontend Interface (The Body)
- [x] **Split-Screen Layout:** Left panel for Chat, Right panel for Project Board.
- [x] **Project Sidebar:** Lists historical projects from Firestore (`project_boards` collection), allowing users to switch contexts.
- [x] **URL-Based State:** The active project is determined by `?threadId=...` in the URL. Reloading restores context.
- [x] **Real-Time Board:** The Right Panel updates automatically via Firestore `onSnapshot` when the Architect updates the plan.

## 3. Capabilities (The Hands)
- [x] **Download Source:** A "Download" button on the Board triggers a backend endpoint (`/agent/download/{thread_id}`) to zip and serve the GCS files.
- [x] **Plan Generation:** The Architect Agent creates and updates a `master_plan.md` file.
- [x] **Strict Pathing:** Frontend Agent is trained to strictly write to `frontend/` paths (though currently writing to GCS, ensuring no local ghost files).

## 4. Known Constraints (The Rules)
- [ ] **No Local File Writes:** Agents do not write to the local container disk anymore; they only write to GCS.
- [ ] **No Nested Frontends:** We must ensure future commands do not create `frontend/frontend/` artifacts.