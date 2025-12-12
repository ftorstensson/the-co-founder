# FEATURE LEDGER

## CORE CAPABILITIES (PROTECTED)
- [x] **Voice Interface:** "Walkie-Talkie" style audio recording. Sends raw audio to Gemini (Multimodal) for tone/context analysis. No text-transcription middleware.
- [x] **The "Scribe" Engine:** Background agent extracting Vision/Tasks.
- [x] **The "Proxy" Data Layer:** Robust Server-Side fetching for Sidebar and Board.
- [x] **Auto-Pilot Mode:** Instant save and update.

## INTERFACE
- **Voice Recorder:** Visual feedback (Pulse Red), handles browser permissions seamlessly.
- **Workspace Sidebar:** Sort by Pinned, Context Menu (Rename/Delete/Pin).
- **Knowledge Board:** Live-updating Vision and Roadmap.

## INFRASTRUCTURE
- **Dual-Model Brain:** Pro (Chat), Flash (Scribe).
- **Bare Metal Persistence:** Custom Firestore serialization.