import subprocess
import re
import os

# ================= CONFIGURATION: YOUR CODING GUIDELINES =================
# Add or remove rules here. 
# Format: ("Rule Name", r"Regex Pattern to INVALIDATE", "Error Message")
C_SHARP_RULES = [
    (
        "No Console.WriteLine", 
        r"Console\.WriteLine", 
        "Avoid leaving 'Console.WriteLine' in production code. Use a Logger."
    ),
    (
        "Naming: Private Fields", 
        r"private\s+\w+\s+(?![_])[a-z]", 
        "Private fields should start with an underscore (e.g., '_myVar')."
    ),
    (
        "Naming: Async Methods", 
        r"\s+async\s+Task.*(?<!Async)\s*\(", 
        "Async methods should end with the suffix 'Async' (e.g., 'GetDataAsync')."
    ),
    (
        "Naming: Method PascalCase", 
        r"\s+void\s+[a-z][a-zA-Z0-9]*\(", 
        "Method names must be PascalCase (e.g., 'CalculateTotal', not 'calculateTotal')."
    ),
    (
        "No Hardcoded Paths", 
        r'"[C-Zc-z]:\\', 
        "Do not use hardcoded absolute Windows paths."
    ),
    (
        "Comment Requirement", 
        r"^\s*//\s*TODO", 
        "You left a TODO comment. Please resolve it before merging."
    )
]
# =========================================================================

def get_git_diff_output():
    """
    Runs 'git diff' to get uncommitted changes.
    Use 'git diff HEAD~1' to check the last committed changes instead.
    """
    try:
        # Get changes in the working directory (staged and unstaged)
        result = subprocess.run(
            ["git", "diff", "HEAD", "--unified=0"], 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.stdout
    except FileNotFoundError:
        print("Error: Git is not installed or this is not a git repository.")
        return ""

def parse_diff_and_check_rules(diff_output):
    current_file = None
    line_number = 0
    violations = []

    # Regex to identify file headers in git diff
    file_header_pattern = re.compile(r"^\+\+\+ b/(.*)")
    # Regex to identify hunk headers (e.g., @@ -10,0 +15,3 @@) to track line numbers
    hunk_header_pattern = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

    for line in diff_output.splitlines():
        # 1. Detect File Switch
        file_match = file_header_pattern.match(line)
        if file_match:
            current_file = file_match.group(1)
            continue

        # 2. Detect Line Number Changes (Hunks)
        hunk_match = hunk_header_pattern.match(line)
        if hunk_match:
            line_number = int(hunk_match.group(1))
            continue

        # 3. Process Added/Modified Lines (Lines starting with + but not +++ header)
        if line.startswith("+") and not line.startswith("+++"):
            actual_code = line[1:] # Remove the "+" symbol
            
            # Skip checking comments or empty lines if you want
            if not actual_code.strip() or actual_code.strip().startswith("//"):
                line_number += 1
                continue

            # CHECK RULES
            # Only check C# files
            if current_file and current_file.endswith(".cs"):
                for rule_name, pattern, message in C_SHARP_RULES:
                    if re.search(pattern, actual_code):
                        violations.append({
                            "file": current_file,
                            "line_num": line_number,
                            "code": actual_code.strip(),
                            "message": message
                        })
            
            line_number += 1

    return violations

def print_report(violations):
    print("\n INCREMENTAL CODE GUIDELINE CHECKER")
    print("=======================================")
    
    if not violations:
        print("No issues found in your recent changes. Good job!")
        return

    print(f"Found {len(violations)} issues in your changed lines:\n")
    
    current_file = ""
    for v in violations:
        if v["file"] != current_file:
            print(f"File: {v['file']}")
            current_file = v["file"]
        
        print(f"   Line {v['line_num']}: {v['code']}")
        print(f"   ↳ {v['message']}")
        print("")
    
    print("=======================================")
    print("Fix these specific lines before committing.")

if __name__ == "__main__":
    diff_output = get_git_diff_output()
    if diff_output:
        issues = parse_diff_and_check_rules(diff_output)
        print_report(issues)
    else:
        print("No changes detected. Make sure you have modified files in your repo.")