import chromadb
from chromadb.utils import embedding_functions
import json
import os

# Initialize ChromaDB
# For the hackathon, we use a simple persistent local store
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")
client = chromadb.PersistentClient(path=DB_PATH)

# Force keyword search for hackathon stability due to environment mismatches
USE_VECTOR = False
try:
    collection = client.get_or_create_collection(name="exercises_fallback")
except Exception as e:
    print(f"Collection initialization error: {e}")

def populate_knowledge_base():
    """Seed the database with initial exercise data."""
    json_path = os.path.join(os.path.dirname(__file__), "exercises.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found")
        return
        
    with open(json_path, 'r') as f:
        exercises = json.load(f)
        
    print(f"Inserting {len(exercises)} exercises...")
    for ex in exercises:
        text = f"{ex['name']}: {ex['description']} Targets: {', '.join(ex['muscles'])}. Equipment: {', '.join(ex['equipment'])}."
        
        upsert_params = {
            "ids": [ex['id']],
            "documents": [text],
            "metadatas": [{
                "name": ex['name'],
                "difficulty": ex['difficulty'],
                "equipment": json.dumps(ex['equipment']),
                "muscles": json.dumps(ex['muscles'])
            }]
        }
        
        # If not using vector EF, we MUST provide embeddings
        if not USE_VECTOR:
            upsert_params["embeddings"] = [[0.0] * 384]
            
        collection.upsert(**upsert_params)

def search_exercises(query: str, n_results: int = 3):
    """Retrieve exercises with a fallback for systems without onnxruntime."""
    try:
        if USE_VECTOR:
            results = collection.query(query_texts=[query], n_results=n_results)
            
            search_results = []
            if results.get('documents') and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    search_results.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
            return search_results
        else:
            # PURE PYTHON FALLBACK: Load from JSON directly for absolute stability
            json_path = os.path.join(os.path.dirname(__file__), "exercises.json")
            if not os.path.exists(json_path):
                return []
                
            with open(json_path, 'r') as f:
                exercises = json.load(f)
            
            matches = []
            q_lower = query.lower()
            for ex in exercises:
                score = 0
                text = f"{ex['name']} {ex['description']} {' '.join(ex['muscles'])} {' '.join(ex['equipment'])}".lower()
                for word in q_lower.split():
                    if word in text: score += 1
                if score > 0:
                    matches.append((ex, score))
            
            # Sort by score and take top N
            matches.sort(key=lambda x: x[1], reverse=True)
            search_results = []
            for ex, score in matches[:n_results]:
                search_results.append({
                    "id": ex['id'],
                    "document": f"{ex['name']}: {ex['description']}",
                    "metadata": {
                        "name": ex['name'],
                        "difficulty": ex['difficulty'],
                        "equipment": json.dumps(ex['equipment']),
                        "muscles": json.dumps(ex['muscles'])
                    }
                })
            return search_results
            
    except Exception as e:
        print(f"Search error: {e}")
        return []

# Initialize on import
if __name__ == "__main__":
    populate_knowledge_base()
    print("Knowledge base populated.")
