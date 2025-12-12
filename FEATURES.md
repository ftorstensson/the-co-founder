# FEATURE LEDGER

## CORE CAPABILITIES (PROTECTED)
- **The "Scribe" Engine:** A background `gemini-2.5-flash` agent that silently reads conversation history and updates a structured JSON object in Firestore (Vision, Tasks, Files).
- **The "Proxy" Data Layer:** Frontend fetches data via Backend API (`/agent/projects`), bypassing client-side firewall issues.
- **Auto-Pilot Mode:** No "Save" button required. The system saves on every user interaction.

## INTERFACE
- **Workspace Sidebar:**
    - Sorts by Pinned, then Date.
    - 3-Dot Context Menu (Rename, Pin, Delete).
    - Optimistic UI updates (Instant feedback before server confirms).
- **Knowledge Board:**
    - Live-updating Vision Statement.
    - Dynamic Task List (Todo/Done states).
    - File Artifact tracking.

## INFRASTRUCTURE
- **Dual-Model Brain:** Pro for Chat, Flash for Tasks.
- **Bare Metal Persistence:** Custom Firestore serialization (No LangChain checkpoint libraries).
- **Docker Build-Args:** Environment variables baked in at build time for production stability.