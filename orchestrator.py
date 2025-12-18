import subprocess
import json
import os

# ================= CONFIGURATION =================
# 1. PASTE THE PATH from your screenshot below.
#    (Use "r" before the string to handle backslashes safely)
TARGET_SOURCE_CODE_FOLDER = r"C:\Users\pradipti.sah\Downloads\AstProject\ESCPOS_NET"

# 2. Path to your compiled C# tool (AstExtractor)
#    We assume it's still in the same folder as this python script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "AstExtractor")
# =================================================

def get_csharp_ast(file_path):
    """Calls the compiled C# app to parse .cs files"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        # Run the C# tool
        result = subprocess.run(
            ["dotnet", "run", "--project", PROJECT_DIR, file_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Common error: build failures or bad paths
            return {"error": "C# process failed", "details": result.stderr.strip()}
            
        if not result.stdout.strip():
            return {"error": "Empty output from C#"}

        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

# Main Execution
print(f"Scanning folder: {TARGET_SOURCE_CODE_FOLDER}")

all_asts = {}
file_count = 0

# os.walk automatically goes into ALL subfolders (recursively)
for root, dirs, files in os.walk(TARGET_SOURCE_CODE_FOLDER):
    
    # OPTIONAL: Skip 'bin' and 'obj' folders to speed things up
    # (These usually contain auto-generated junk code)
    dirs[:] = [d for d in dirs if d not in ['bin', 'obj', '.git', '.vs']]

    for file in files:
        if file.endswith(".cs"):
            full_path = os.path.join(root, file)
            print(f"   Processing: {file}...")
            
            ast_data = get_csharp_ast(full_path)
            
            # Save using the full path as the key so you know where it came from
            all_asts[full_path] = {
                "language": "csharp",
                "ast": ast_data
            }
            file_count += 1

# Save the final result
output_file = "full_project_ast.json"
with open(output_file, "w") as f:
    json.dump(all_asts, f, indent=4)

print("-" * 50)
print(f"Done! Processed {file_count} C# files.")
print(f"AST saved to: {output_file}")