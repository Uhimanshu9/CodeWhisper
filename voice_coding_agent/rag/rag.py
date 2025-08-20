import os
import hashlib
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, PointsSelector, VectorParams, Distance
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import tool
from qdrant_client.http.models import PointsSelector


# Config
INDEX_FILE = "index_metadata.json"
COLLECTION_NAME = "project_code"

# Initialize embeddings + Qdrant
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
VECTOR_SIZE = 768  # Gemini embeddings dimension (models/embedding-001)
qdrant = QdrantClient(":memory:")  # swap with persistent Qdrant server if needed

# Ensure collection exists
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
)

def file_hash(path: str) -> str:
    """Compute MD5 hash of a file."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def stable_id(path: str) -> int:
    """Generate stable ID for Qdrant from file path (instead of Python hash)."""
    return int(hashlib.md5(path.encode()).hexdigest(), 16) % (10**12)

def load_metadata():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    return {}

def save_metadata(meta):
    with open(INDEX_FILE, "w") as f:
        json.dump(meta, f, indent=2)

def reindex_file(path: str):
    """Reindex a file into Qdrant using Gemini embeddings."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Compute embedding vector for the file content
    vec = embeddings.embed_query(content)

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=stable_id(path),
                vector=vec,
                payload={"path": path, "content": content}
            )
        ]
    )
    return f"Reindexed {path}"

@tool
def update_project_index(root: str = ".", force: bool = False) -> str:
    """
    Incrementally update project index by hashing files.
    Only changed files are re-embedded unless `force=True`.
    Also cleans up deleted files from metadata.
    """
    metadata = {} if force else load_metadata()
    updated_files = []

    # --- cleanup: remove metadata for deleted files ---
    for path in list(metadata.keys()):
        if not os.path.exists(path):
           qdrant.delete(
                collection_name=COLLECTION_NAME,
                points_selector=PointsSelector(ids=[stable_id(path)])
            )
           del metadata[path]

    # --- scan current files ---
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if not f.endswith((".py", ".txt")):  # extend as needed
                continue
            path = os.path.join(dirpath, f)
            h = file_hash(path)

            # reindex if forced, new file, or hash changed
            if force or path not in metadata or metadata[path]["hash"] != h:
                reindex_file(path)
                metadata[path] = {"hash": h}
                updated_files.append(path)

    save_metadata(metadata)
    if updated_files:
        return f"✅ Reindexed {len(updated_files)} file(s):\n" + "\n".join(updated_files)
    return "✅ Index is already up to date."
