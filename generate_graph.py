import json
import csv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

# ================= CONFIGURATION =================
INPUT_FILE = "project_embeddings.json"
NODES_FILE = "nodes.csv"
EDGES_FILE = "edges.csv"

# SIMILARITY THRESHOLD (0.0 to 1.0)
# 0.8 is a good starting point for code similarity. 
# Increase to 0.9 for stricter connections, decrease to 0.7 for more loose connections.
SIMILARITY_THRESHOLD = 0.8 
# =================================================

def generate_graph_csv():
    # 1. Load Embeddings
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    print("Loading embeddings...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        embeddings_map = json.load(f)

    # Convert dictionary to Lists for processing
    files = list(embeddings_map.keys())
    vectors = list(embeddings_map.values())
    
    # Convert to Numpy Array
    print(f"Processing {len(files)} files...")
    vector_matrix = np.array(vectors)

    # 2. Calculate Cosine Similarity Matrix (All-vs-All)
    print("Calculating similarity matrix...")
    similarity_matrix = cosine_similarity(vector_matrix)

    # 3. Write NODES.csv
    # Format: Id, Label, Type
    print(f"Writing {NODES_FILE}...")
    with open(NODES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Id", "Label", "Type"]) # Header
        
        for file_path in files:
            # "Id" is the full path, "Label" is just the file name
            file_name = os.path.basename(file_path)
            writer.writerow([file_path, file_name, "File"])

    # 4. Write EDGES.csv
    # Format: Source, Target, Weight
    print(f"Writing {EDGES_FILE}...")
    edge_count = 0
    
    with open(EDGES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Target", "Weight"]) # Header

        num_files = len(files)
        # Iterate through the upper triangle of the matrix to avoid duplicates and self-loops
        for i in range(num_files):
            for j in range(i + 1, num_files):
                score = similarity_matrix[i][j]
                
                if score >= SIMILARITY_THRESHOLD:
                    source = files[i]
                    target = files[j]
                    
                    # Write the edge
                    writer.writerow([source, target, f"{score:.4f}"])
                    edge_count += 1

    print("-" * 50)
    print(f"Graph generation complete!")
    print(f"   Nodes: {len(files)}")
    print(f"   Edges: {edge_count} (min similarity: {SIMILARITY_THRESHOLD})")
    print(f"Output: {NODES_FILE}, {EDGES_FILE}")

if __name__ == "__main__":
    generate_graph_csv()