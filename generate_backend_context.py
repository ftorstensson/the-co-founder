# --- SECTION A: IMPORTS ---
import os

# --- SECTION B: CONFIGURATION ---
EXTENSIONS = ('.py', '.md', '.txt')
IGNORE_DIRS = {'.venv', '__pycache__', '.git', 'frontend', 'node_modules'}
# Only keep the current seed script (v12)
IGNORE_FILES = {
    'seed_agency_v1.py', 'seed_agency_v2.py', 'seed_agency_v3.py',
    'seed_agency_v4.py', 'seed_agency_v5.py', 'seed_agency_v6.py',
    'seed_agency_v7.py', 'seed_agency_v8.py', 'seed_agency_v9.py',
    'seed_agency_v10.py', 'seed_agency_v11.py', 'generate_backend_context.py'
}

def generate():
    output = ["# BACKEND GROUND TRUTH: THE BRAIN\n"]
    root_dir = os.getcwd()
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(EXTENSIONS) and file not in IGNORE_FILES:
                path = os.path.join(root, file)
                rel = os.path.relpath(path, root_dir)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        output.append(f"\n--- START: {rel} ---\n{f.read()}\n--- END: {rel} ---\n")
                except: pass

    with open("BACKEND_CONTEXT.txt", "w") as f:
        f.write("\n".join(output))
    print("✅ BACKEND_CONTEXT.txt generated.")

if __name__ == "__main__":
    generate()