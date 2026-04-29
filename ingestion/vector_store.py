try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from config.settings import CHROMA_PERSIST_DIR

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Lazy load vector database to avoid Python 3.14 pydantic issues
vectordb = None

def get_vectordb():
    """Get or initialize vector database (lazy loading)"""
    global vectordb
    if vectordb is None:
        try:
            vectordb = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"Warning: Could not initialize Chroma DB: {e}")
            return None
    return vectordb

def store_vector(chunks):
    """Store document chunks in vector database"""
    try:
        db = get_vectordb()
        if db is not None:
            db.add_documents(chunks)
            # Note: Chroma 0.4+ auto-persists, no need to call persist()
            return True
        else:
            print("Error: Vector DB not available")
            return False
    except Exception as e:
        print(f"Error storing vectors: {e}")
        return False
