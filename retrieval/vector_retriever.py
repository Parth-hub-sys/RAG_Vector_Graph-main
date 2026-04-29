try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import os

# Read Chroma persist directory directly from environment
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vectordb")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

vectordb = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=embeddings
)

def vector_search(query: str):
    docs = vectordb.similarity_search(query, k=4)
    return "\n".join([d.page_content for d in docs])
