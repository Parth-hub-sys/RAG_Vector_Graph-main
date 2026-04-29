import os

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Chroma Vector DB Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vectordb")

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Data Configuration
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")
METADATA_FILE = os.getenv("METADATA_FILE", "./metadata/ingested_files.json")

# print(NEO4J_URI)
# print(NEO4J_USER)
# print(NEO4J_PASSWORD)
