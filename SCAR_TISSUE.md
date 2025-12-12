# SCAR TISSUE LEDGER (v3.2 - The Voice Integration)
*Last Updated: 2025-12-13*

This document is the "Black Box Recorder" of our agency.

---

## 1. THE DEPLOYMENT PROTOCOLS (THE CO-FOUNDER)
**STATUS:** ACTIVE
**PROJECT:** The Co-Founder (Knowledge Engine)
**GCP PROJECT:** `vibe-agent-final`
**REGION:** `australia-southeast1`

### A. Backend Deployment (The Brain)
*Targets the `co-founder-backend` service.*
**Command:**
docker build -t australia-southeast1-docker.pkg.dev/vibe-agent-final/vibe-repo/co-founder-backend:latest . && docker push australia-southeast1-docker.pkg.dev/vibe-agent-final/vibe-repo/co-founder-backend:latest && gcloud run deploy co-founder-backend --image australia-southeast1-docker.pkg.dev/vibe-agent-final/vibe-repo/co-founder-backend:latest --region australia-southeast1 --project vibe-agent-final --allow-unauthenticated

### B. Frontend Deployment (The Interface)
*Targets the `co-founder-frontend` service. Requires Build-Time Args.*
**Command:**
docker build --no-cache --build-arg NEXT_PUBLIC_API_URL=https://co-founder-backend-534939227554.australia-southeast1.run.app --build-arg NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCK-8ucH5Ncri5d9px2DSJ7Vrk1Y0O4PYw --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=vibe-agent-final.firebaseapp.com --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID=vibe-agent-final --build-arg NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=vibe-agent-final.firebasestorage.app --build-arg NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=534939227554 --build-arg NEXT_PUBLIC_FIREBASE_APP_ID=1:534939227554:web:0bed74dd458e849c028efb -t australia-southeast1-docker.pkg.dev/vibe-agent-final/vibe-repo/co-founder-frontend:latest frontend/ && docker push australia-southeast1-docker.pkg.dev/vibe-agent-final/vibe-repo/co-founder-frontend:latest && gcloud run deploy co-founder-frontend --image australia-southeast1-docker.pkg.dev/vibe-agent-final/vibe-repo/co-founder-frontend:latest --region australia-southeast1 --project vibe-agent-final --allow-unauthenticated

---

## 2. THE SCAR TISSUE LEDGER (LESSONS LEARNED)

**Entry 024: The Audio Blob Bridge**
*   **Problem:** Sending audio from Browser to Python Backend to Vertex AI without writing temp files.
*   **Solution:**
    1.  **Frontend:** `MediaRecorder` -> `Blob` -> `FormData` (`file`).
    2.  **Backend:** `UploadFile` -> `await file.read()` -> `base64` encode.
    3.  **Vertex:** `HumanMessage(content=[{"type": "media", "data": b64_data}])`.
    *   **Note:** Do NOT try to send raw bytes directly to LangChain. Base64 is the required transport format.

**Entry 023: The Client-Side Firestore Mirage**
*   **Symptom:** Application works perfectly on `localhost`, but Sidebar and Data are empty in Cloud Run.
*   **Diagnosis:** Direct Firebase Client SDK connections (`onSnapshot`) are fragile in Cloud environments due to strict firewall/CORS policies and "Build Time vs. Run Time" variable confusion.
*   **Fix:** **The Robust API Proxy.** Do not let the Frontend talk to the DB directly. Make the Frontend ask the Backend (`GET /agent/projects`), and let the Backend (running in a privileged cloud container) fetch the data. It is 100% reliable.

**Entry 022: The Docker Disk Exhaustion (Input/Output Error)**
*   **Symptom:** Docker builds fail with 'write /var/lib/docker/...: input/output error'.
*   **Diagnosis:** Frequent builds fill the Docker VM disk image.
*   **Fix:** Run `docker system prune -a --volumes -f` immediately.

**Entry 021: The "Ghost File" Hallucination**
*   **Symptom:** Agent claims to write files but they don't appear.
*   **Diagnosis:** Agent defaults to Root (`/app`) instead of `frontend/`.
*   **Fix:** Explicitly instruct: "You MUST prefix all paths with `frontend/`."

**Entry 020: The Gemini Protocol Violation (AI->AI Crash)**
*   **Symptom:** `500 Internal Server Error` during delegation.
*   **Diagnosis:** Gemini forbids `AI -> AI` turns.
*   **Fix:** **"Virtual User" Pattern.** Wrap Worker output in `HumanMessage(name="WorkerName")`.

**Entry 019: The Firestore Composite Index Barrier**
*   **Symptom:** `400 The query requires an index`.
*   **Fix:** Click the link in the error message to build the index. Never guess.

**Entry 018: The "Model Retirement" Trap**
*   **Symptom:** `404 Not Found` for `gemini-1.5-pro`.
*   **Fix:** Use `gemini-2.5-pro` and `gemini-2.5-flash`.

**Entry 017: The Next.js Build-Time Variable Trap**
*   **Symptom:** Frontend connects to localhost in production.
*   **Diagnosis:** `NEXT_PUBLIC_` vars are baked at build time.
*   **Fix:** Use `--build-arg NEXT_PUBLIC_API_URL=...` in the `docker build` command.

**Entry 016: The Next.js 15 Linting Blockade**
*   **Symptom:** Build fails on "Element has no title attribute".
*   **Fix:** Always add `aria-label="Description"` to icon-only buttons.

**Entry 015: The "Nested Agent" Recursion Loop**
*   **Symptom:** Infinite loop of delegations.
*   **Fix:** Sub-agents must route to `END`, not back to Supervisor.

**Entry 014: The "Consecutive AI Message" Crash**
*   **Symptom:** `400 Please ensure number of function response parts...`.
*   **Fix:** Supervisor must inject a `HumanMessage` when delegating, not an `AIMessage`.

**Entry 013: The Gemini "Silent Refusal"**
*   **Symptom:** Empty string output with 0 tokens.
*   **Fix:** Use `.with_structured_output(Schema)` and `temperature=0.1`.

**Entry 012: The `FixedFirestoreSaver` Bug**
*   **Symptom:** `TypeError: sequence item 2: expected str instance`.
*   **Fix:** Ensure `checkpoint_id` is generated if `None` before saving.

**Entry 011: The Supervisor's Infinite Loop**
*   **Diagnosis:** Supervisor sees a tool output and re-delegates.
*   **Fix:** Prompt must say: "If last message is TOOL response -> Summarize and FINISH."

**Entry 010: The Docker "Input/Output Error" Paradox**
*   **Diagnosis:** Corrupted Docker Desktop environment.
*   **Fix:** Factory Reset Docker Desktop.

**Entry 009: The Gemini `BaseMessage` Rejection**
*   **Diagnosis:** Gemini rejects `ToolMessage` in history.
*   **Fix:** Sanitize history to convert `ToolMessage` to `HumanMessage` before sending to Supervisor.

**Entry 008: The `ModuleNotFoundError` Cascade**
*   **Diagnosis:** Version mismatch.
*   **Fix:** Use a pinned, known-good `requirements.txt`.

**Entry 007: The LangServe `config_keys` Paradox**
*   **Diagnosis:** `config_keys` strips the checkpoint config.
*   **Fix:** NEVER use `config_keys` in `add_routes` with a checkpointer.

**Entry 006: The Environmental Parity Failure**
*   **Fix:** **Local Push Protocol.** Build locally, tag, push, then deploy.

**Entry 001-005:** (Legacy) Gunicorn/FastAPI mismatch, CLI hallucinations, ADK abandonment.