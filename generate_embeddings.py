import json
import os
from openai import AzureOpenAI

# ================= CONFIGURATION =================
AZURE_OPENAI_API_KEY = "9027cf1866e745218ac40a579914e2c9"  # Ensure this is your full key
AZURE_OPENAI_ENDPOINT = "https://da-azurerm-cognitive-account-internal-uat.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2023-05-15"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Initialize Client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

INPUT_FILE = "full_project_ast.json"
OUTPUT_FILE = "project_embeddings.json"

# Token limit for ada-002 is 8192 tokens. 
# 1 token ~= 4 chars. Safe limit is ~30,000 chars.
SAFE_CHAR_LIMIT = 50000 

def get_embedding(text, file_label):
    """Helper to call API and handle content"""
    # Ensure we don't send empty text
    if not text or not text.strip():
        return None
        
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def generate_embeddings():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    embeddings_map = {}
    print(f"Loaded AST for {len(data)} files. Starting process...")

    for file_path, file_data in data.items():
        vector = None
        
        # --- STRATEGY 1: Try Full AST JSON ---
        try:
            # Minify JSON to save space
            ast_text = json.dumps(file_data['ast'], separators=(',', ':'))
            print(f"🔹 Processing: {file_path} (AST Size: {len(ast_text)} chars)...")
            
            vector = get_embedding(ast_text, file_path)
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if error is about Token Limit (Context Length)
            if "context length" in error_msg or "too long" in error_msg:
                print(f"AST too large. Retrying with RAW CODE...")
                
                # --- STRATEGY 2: Try Raw Source Code ---
                try:
                    # Extract raw text from the root of the AST
                    raw_code = file_data['ast'].get('text', '')
                    vector = get_embedding(raw_code, file_path)
                    print(f"Success with Raw Code.")
                    
                except Exception as e2:
                    error_msg2 = str(e2).lower()
                    if "context length" in error_msg2:
                        print(f"Raw Code too large. Retrying with TRUNCATION...")
                        
                        # --- STRATEGY 3: Truncate Raw Code ---
                        try:
                            # Slice the text to the safe limit
                            safe_text = file_data['ast'].get('text', '')[:SAFE_CHAR_LIMIT]
                            vector = get_embedding(safe_text, file_path)
                            print(f"Success with Truncated Code ({SAFE_CHAR_LIMIT} chars).")
                        except Exception as e3:
                            print(f"Failed to embed {file_path}: {e3}")
                    else:
                        print(f"Error with Raw Code: {e2}")
            else:
                print(f"Unexpected Error: {e}")

        # Save result if successful
        if vector:
            embeddings_map[file_path] = vector

    # Save to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(embeddings_map, f)

    print("-" * 50)
    print(f"Finished! Generated {len(embeddings_map)} embeddings.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_embeddings()