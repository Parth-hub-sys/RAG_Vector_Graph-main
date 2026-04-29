import os
import hashlib
import json
import logging

from ingestion.loader import load_document
from ingestion.chunker import chunk_documents
from ingestion.vector_store import store_vector
from ingestion.extractor import extract_triplets
from ingestion.graph_store import store_graph
from agent.rag_agent import answer
from config.settings import DATA_FOLDER, METADATA_FILE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

META_FILE = METADATA_FILE


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load_metadata():
    if not os.path.exists(META_FILE):
        return []
    with open(META_FILE, "r") as f:
        return json.load(f)


def save_metadata(data):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=2)


def ingest_all():
    print("\n📥 Starting ingestion...\n")

    if not os.path.exists(DATA_FOLDER):
        print(f"⚠️ Data folder not found: {DATA_FOLDER}")
        print("📁 Please add PDF files to the data folder and try again.\n")
        return

    processed = load_metadata()
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(('.pdf', '.txt'))]
    
    if not files:
        print("⚠️ No documents found in data folder.")
        print("📁 Please add PDF or TXT files to the data folder.\n")
        return

    for file in files:
        path = os.path.join(DATA_FOLDER, file)
        h = file_hash(path)

        if h in processed:
            print(f"⏭ Skipping duplicate: {file}")
            continue

        try:
            print(f"Ingesting: {file}")

            docs = load_document(path)
            chunks = chunk_documents(docs)

            # Store in vector DB (required)
            vec_success = store_vector(chunks)
            if vec_success:
                print(f"  ✓ Stored in vector DB")
            else:
                print(f"  ✗ Failed to store in vector DB")
                continue

            # Store in graph DB (optional)
            graph_count = 0
            for chunk in chunks:
                triplets = extract_triplets(chunk.page_content)
                graph_count += store_graph(triplets)
            
            if graph_count > 0:
                print(f"  ✓ Stored {graph_count} relationships in graph DB")
            else:
                print(f"  ℹ Graph storage skipped or unavailable")

            processed.append(h)
        
        except Exception as e:
            logger.error(f"Error ingesting {file}: {e}")
            continue

    save_metadata(processed)

    print("\n✅ Ingestion complete!\n")


def chat_loop():
    print("\n" + "="*60)
    print("🤖 RAG SYSTEM READY")
    print("="*60)
    print("✓ Vector Search: ACTIVE")
    print("✓ Graph Search: CHECKING...")
    print("\nType 'exit' to quit")
    print("="*60 + "\n")

    while True:
        try:
            query = input("You: ").strip()

            if query.lower() == "exit":
                print("\nGoodbye! 👋\n")
                break
            
            if not query:
                continue

            print("\n🔍 Searching...\n")
            response = answer(query)
            print("AI:", response, "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print("❌ Error processing query. Please try again.\n")


if __name__ == "__main__":
    ingest_all()
    chat_loop()
