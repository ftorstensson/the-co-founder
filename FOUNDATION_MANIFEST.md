# THE AGENT FOUNDATION (v1.0)
*A Production-Grade Starter Kit for Agentic SaaS Applications*

## 1. The Executive Summary
This repository contains a fully functional, cloud-native infrastructure for building **Multi-Agent AI Applications**. It solves the hard problems of state management, memory, real-time UI updates, and LLM protocol compatibility out of the box.

**It is domain-agnostic.** By changing the "DNA" (Database Prompts) and "Hands" (Python Tools), this system can transform from a **Coding Agency** into a **Legal Firm**, **Travel Concierge**, or **Research Bureau** in minutes.

---

## 2. The Architecture (The "Genesis Engine")

### **The Brain (Backend)**
*   **Tech:** Python, FastAPI, LangGraph.
*   **Intelligence:** Hybrid Architecture.
    *   **Supervisor (PM):** Gemini 2.5 Pro (High Reasoning/EQ).
    *   **Workers:** Gemini 2.5 Flash (High Speed/Execution).
*   **Protocol:** "Linear Delegation" with "Virtual User" patterns to prevent API crashes.
*   **Memory:** Custom Firestore implementation with Time-Sortable IDs (No Amnesia).

### **The Body (Frontend)**
*   **Tech:** Next.js 15 (App Router), Tailwind CSS, Lucide React.
*   **State:** URL-Based Session Persistence (\`?threadId=...\`).
*   **Real-Time:** Firestore \`onSnapshot\` listeners for instant UI updates (The "Project Board").

### **The Storage (Memory & Artifacts)**
*   **Context:** Google Firestore (Conversation History & Project State).
*   **Workspace:** Google Cloud Storage (File persistence & Downloads).

---

## 3. How to Pivot (The "Factory" Model)
To turn this foundation into a new product (e.g., "The Legal Eagle"), follow these steps:

### **Step A: Change the DNA (Prompts)**
1.  Open \`seed_agents.py\`.
2.  Rename \`head_of_frontend\` to \`senior_legal_researcher\`.
3.  Change the System Prompt: *"You are a lawyer. Draft contracts based on the user's request..."*
4.  Run \`python seed_agents.py\` to update the Brain.

### **Step B: Change the Hands (Tools)**
1.  Open \`app/tools.py\`.
2.  Replace \`write_file\` (coding) with domain-specific tools (e.g., \`search_case_law\`, \`send_email\`, \`generate_pdf\`).
3.  Update \`app/chain.py\` to bind these new tools to the Worker Agent.

### **Step C: Update the Board (UI)**
1.  Open \`frontend/components/ProjectBoard.tsx\`.
2.  Change the visualization to match the new domain (e.g., instead of "Code Tasks", show "Contract Clauses").

---

## 4. The "Iron Dome" (Stability Guarantees)
This foundation includes protections against common AI failures:
*   **Infinite Loops:** The Graph Topology enforces a \`Supervisor -> Worker -> End\` flow.
*   **Hallucinations:** Strict Pydantic Output Parsers force the Supervisor to choose valid paths.
*   **Protocol Errors:** The \`GeminiToolAdapter\` automatically sanitizes history to prevent 500 Errors.
*   **Docker Rot:** Includes auto-pruning documentation to prevent disk exhaustion.

---

## 5. Deployment
*   **Backend:** Dockerized FastAPI on Cloud Run.
*   **Frontend:** Dockerized Next.js (Standalone) on Cloud Run.
*   **CI/CD:** Use the "Deploy Command" in \`SCAR_TISSUE.md\` to push updates.

**Current Version Tag:** \`v1-foundation\`