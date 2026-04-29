# RAG-agent
# RAG System Setup Guide

## Quick Start

### 1. Configure Environment Variables
Copy `.env.example` to `.env` and update with your credentials:
```bash
cp .env.example .env
```

Edit `.env` and add:
- Your Neo4j password (must match docker-compose.yml)
- Your Groq API key (for LLM responses)

---

## Option A: Docker Setup (Recommended)

### Prerequisites
- Docker and Docker Compose installed

### Steps
1. **Update docker-compose.yml**
   - Change `NEO4J_AUTH: neo4j/your_secure_password_here` to your desired password
   - Match this password in your `.env` file

2. **Start Neo4j**
   ```bash
   docker-compose up -d
   ```

3. **Wait for Neo4j to start** (check health)
   ```bash
   docker-compose ps
   ```

4. **Access Neo4j Browser**
   - Open: http://localhost:7474
   - Login with: `neo4j` / `your_password`

5. **Verify Connection**
   - Run your RAG application:
   ```bash
   python run.py
   ```

---

## Option B: Local Neo4j Installation

### Windows
1. Download Neo4j Desktop from https://neo4j.com/download/
2. Install and create a new database
3. Set password during setup
4. Start the database
5. Update `.env` with your credentials

### Verify Connection
```bash
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password')); print('Connected!')"
```

---

## System Architecture

### Vector Search (Always Active)
- Uses Chroma DB with HuggingFace embeddings
- Extracts semantic meaning from documents
- Works offline, fast retrieval

### Graph Search (Optional but Recommended)
- Uses Neo4j to store entity relationships
- Extracts knowledge triplets (Subject → Relationship → Object)
- Enhances answers with structured knowledge

### Hybrid Retrieval
The system now automatically:
1. ✓ Tries vector search
2. ✓ Tries graph search
3. ✓ If both work → Merges results for comprehensive answers
4. ✓ If one fails → Uses the working source
5. ✓ If both fail → Reports what's needed

---

## Workflow

1. **Ingestion Phase**
   - PDF documents are loaded from `./data/`
   - Split into chunks
   - Stored in vector DB (Chroma)
   - Entities and relationships extracted
   - Stored in knowledge graph (Neo4j)

2. **Query Phase**
   - User asks a question
   - Vector DB returns semantically similar documents
   - Graph DB returns relevant entity relationships
   - Both results merged and sent to LLM (Groq)
   - LLM synthesizes comprehensive answer

---

## Troubleshooting

### "Neo4j connection error: Unauthorized"
- Check Neo4j is running
- Verify credentials in `.env` match Neo4j
- If using Docker: `docker-compose logs neo4j`

### "Graph search returned no results"
- Documents need to be re-ingested for graph to populate
- Run: `python run.py` (will ingest documents)
- Check Neo4j browser to see populated data

### "Vector search returned no results"
- Ensure documents exist in `./data/`
- Check `./vectordb/` directory is not empty
- Re-run ingestion if needed

### Slow responses
- Neo4j memory settings need tuning (see docker-compose.yml)
- Vector DB indexing may take time on first query
- LLM API may have latency

---

## Next Steps

1. ✅ Set up `.env` with your credentials
2. ✅ Choose Docker or local Neo4j installation
3. ✅ Run ingestion: `python run.py`
4. ✅ Ask questions and enjoy hybrid retrieval!

For questions, check the error logs and verify both databases are connected.
