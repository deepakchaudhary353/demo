import json
import os
import glob

# ================= CONFIGURATION =================
INPUT_FOLDER = "Jira_Tickets"        # Where your .txt files are
OUTPUT_FOLDER = "Jira_Parsed_JSON"   # Where the .json files will go
# =================================================

def parse_single_jira_file(file_path):
    """
    Parses a single text file and returns the structured dictionary.
    """
    data = {
        "filename": os.path.basename(file_path),
        "metadata": {},
        "content": {},
        "code_location": {},
        "attachments": []
    }
    
    # Parsing Rules
    single_line_keys = [
        "Ticket ID", "Summary", "Environment", "Version", 
        "Priority", "Status", "Assignee", "Reporter", "Created", "Updated"
    ]
    multi_line_keys = [
        "Description", "Observed Behavior", "Expected Behavior", 
        "Error Pattern", "Logs Snippet", "Stack Trace"
    ]
    code_loc_keys = [
        "Repository", "Branch", "Commit ID", "File Path", 
        "Namespace", "Class", "Method", "Lines"
    ]

    current_section = None
    current_key = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f if line.strip()]

        for line in lines:
            # 1. Handle Sections
            if line == "Code Location:":
                current_section = "code_location"
                continue
            if line == "Attachments:":
                current_section = "attachments"
                continue

            # 2. Single Line Metadata
            matched_single = False
            for key in single_line_keys:
                if line.startswith(f"{key}:"):
                    value = line.split(":", 1)[1].strip()
                    data["metadata"][key] = value
                    current_section = None
                    matched_single = True
                    break
            if matched_single: continue

            # 3. Code Location Fields
            if current_section == "code_location":
                for key in code_loc_keys:
                    if line.startswith(f"{key}:"):
                        value = line.split(":", 1)[1].strip()
                        data["code_location"][key] = value
                        matched_single = True
                        break
                if matched_single: continue

            # 4. Multi-Line Headers
            matched_multi = False
            for key in multi_line_keys:
                if line == f"{key}:":
                    current_key = key
                    current_section = "multi_line"
                    data["content"][current_key] = []
                    matched_multi = True
                    break
            if matched_multi: continue

            # 5. Content Processing
            if current_section == "multi_line" and current_key:
                data["content"][current_key].append(line)
            elif current_section == "attachments":
                if line.startswith("- "):
                    data["attachments"].append(line[2:])

        # Join multi-line lists into strings
        for key in data["content"]:
            data["content"][key] = "\n".join(data["content"][key])

        return data

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def process_batch():
    # 1. Check/Create Folders
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"Created folder '{INPUT_FOLDER}'. Please put your .txt files there.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder '{OUTPUT_FOLDER}'.")

    # 2. Find all .txt files
    txt_files = glob.glob(os.path.join(INPUT_FOLDER, "*.txt"))
    
    if not txt_files:
        print(f"No .txt files found in '{INPUT_FOLDER}'.")
        return

    print(f"Found {len(txt_files)} text files. Processing individually...")

    count = 0
    # 3. Loop through every file
    for file_path in txt_files:
        base_name = os.path.basename(file_path)
        print(f"   🔹 Processing: {base_name}")
        
        parsed_data = parse_single_jira_file(file_path)
        
        if parsed_data:
            # Create the JSON filename (e.g., Ticket1.txt -> Ticket1.json)
            json_filename = base_name.replace('.txt', '.json')
            output_path = os.path.join(OUTPUT_FOLDER, json_filename)
            
            # Save INDIVIDUALLY
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=4)
            
            count += 1

    print("-" * 50)
    print(f"Success! Generated {count} JSON files.")
    print(f"Check the folder: {OUTPUT_FOLDER}")

if __name__ == "__main__":
    process_batch()