# FEATURE LEDGER

## CORE CAPABILITIES (PROTECTED)
- [x] **Voice Interface:** "Walkie-Talkie" style audio recording. Sends raw audio to Gemini (Multimodal).
- [x] **The "Scribe" Engine:** Background agent extracting Vision/Tasks.
- [x] **The "Proxy" Data Layer:** Robust Server-Side fetching for Sidebar and Board.
- [x] **The "Truth" Layer:** Identity Modal allows reading/writing `USER_PROFILE.md` directly from the UI.
- [x] **Auto-Pilot Mode:** Instant save and update.

## INTERFACE (MOBILE FIRST)
- **Center Stage UI:** Single-column chat layout optimized for focus.
- **Responsive Drawer:** Sidebar slides in on mobile, stays visible on wide desktops.
- **Identity Editor:** Modal for editing user context/bio.
- **Voice Recorder:** Visual feedback (Pulse Red).

## INTERNAL TOOLS
- **The Design Lab:** (`/design-lab`) A living style guide and prototyping sandbox.
    - **Wireframe Toggle:** Instantly switch between "Skeleton" (Layout) and "Vibe" (Style) modes.
    - **Component Zoo:** Isolated testing ground for Atoms, Molecules, and Organisms.

## INFRASTRUCTURE
- **Dual-Model Brain:** Pro (Chat), Flash (Scribe).
- **Bare Metal Persistence:** Custom Firestore serialization.
- **Cloud Storage:** User profiles stored as raw Markdown (`USER_PROFILE.md`) for portability.