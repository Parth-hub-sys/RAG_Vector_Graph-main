from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(docs):
    """
    Split documents into chunks
    
    Args:
        docs: List of documents to chunk
    
    Returns:
        List of document chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)