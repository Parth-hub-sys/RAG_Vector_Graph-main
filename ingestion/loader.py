from langchain_community.document_loaders import PyPDFLoader,TextLoader,Docx2txtLoader
import os

def load_document(file_path:str):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    docs = loader.load()
    return docs