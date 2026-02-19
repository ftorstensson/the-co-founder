# app/audit.py (Inside 'the-co-founder' folder)
import os

# Get the path to your frontend folder from an environment variable
FRONTEND_ROOT = os.environ.get("FRONTEND_PATH", "../vibe-design-lab")

def generate_code_signature():
    # File paths relative to their respective roots
    backend_targets = ["app/agency/architect.py", "app/agency/departments/product/schemas.py", "app/chain.py"]
    frontend_targets = ["src/app/project/[id]/page.tsx", "src/store/vibe-store.ts", "src/components/StrategyNodes.tsx"]
    
    # NEW: The Ledger location (inside the Frontend Brain folder)
    ledger_path = os.path.join(FRONTEND_ROOT, "Brain/TRUTH_LEDGER.md")
    
    signature = "--- DUAL-REPO CODE SIGNATURE ---\n"
    
    # 1. Audit the Constitution (The Ledger)
    if os.path.exists(ledger_path):
        signature += f"📜 TRUTH LEDGER: DETECTED (Location: Frontend/Brain)\n"
    else:
        signature += f"⚠️ TRUTH LEDGER: MISSING (Expected at: {ledger_path})\n"

    # 2. Audit Backend
    signature += "\n[REPOSITORY: THE-CO-FOUNDER (BACKEND)]\n"
    for path in backend_targets:
        signature += get_file_stats(path)

    # 3. Audit Frontend
    signature += "\n[REPOSITORY: VIBE-DESIGN-LAB (FRONTEND)]\n"
    for path in frontend_targets:
        full_path = os.path.join(FRONTEND_ROOT, path)
        signature += get_file_stats(full_path, display_name=path)
        
    return signature

def get_file_stats(path, display_name=None):
    name = display_name if display_name else path
    if os.path.exists(path):
        with open(path, "r") as f:
            lines = f.readlines()
            return f"FILE: {name} | LINES: {len(lines)}\n"
    return f"FILE: {name} | STATUS: NOT FOUND\n"

if __name__ == "__main__":
    print(generate_code_signature())