import json
import re

def parse_jira_ticket(file_path):
    data = {
        "metadata": {},
        "content": {},
        "code_location": {},
        "attachments": []
    }
    
    # Define parsing rules
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

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f if line.strip()]

    for line in lines:
        # 1. Handle "Code Location" specifically (Nested Object)
        if line == "Code Location:":
            current_section = "code_location"
            continue
        
        # 2. Handle "Attachments" specifically (List)
        if line == "Attachments:":
            current_section = "attachments"
            continue

        # 3. Check for Single Line Metadata (e.g., "Ticket ID: PRINTER-1001")
        # We use strict matching to avoid confusing description text with keys
        matched_single = False
        for key in single_line_keys:
            if line.startswith(f"{key}:"):
                value = line.split(":", 1)[1].strip()
                data["metadata"][key] = value
                current_section = None # Reset section
                matched_single = True
                break
        if matched_single:
            continue

        # 4. Check for Code Location fields (if we are in that section)
        if current_section == "code_location":
            for key in code_loc_keys:
                if line.startswith(f"{key}:"):
                    value = line.split(":", 1)[1].strip()
                    data["code_location"][key] = value
                    matched_single = True
                    break
            if matched_single:
                continue

        # 5. Check for Multi-Line Headers (e.g., "Description:")
        matched_multi = False
        for key in multi_line_keys:
            if line == f"{key}:":
                current_key = key
                current_section = "multi_line"
                data["content"][current_key] = []
                matched_multi = True
                break
        if matched_multi:
            continue

        # 6. Process Content based on current section
        if current_section == "multi_line" and current_key:
            data["content"][current_key].append(line)
            
        elif current_section == "attachments":
            if line.startswith("- "):
                data["attachments"].append(line[2:]) # Remove "- "

    # Post-processing: Join list of lines into single strings for multi-line fields
    for key in data["content"]:
        data["content"][key] = "\n".join(data["content"][key])

    return data

# --- Execution ---
if __name__ == "__main__":
    input_file = "SampleJiraTicket.txt"
    output_file = "StructuredJiraTicket.json"
    
    try:
        parsed_data = parse_jira_ticket(input_file)
        
        # Print to console
        print(json.dumps(parsed_data, indent=4))
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=4)
            
        print(f"\n Successfully saved structured data to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")