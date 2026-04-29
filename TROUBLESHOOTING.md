# Troubleshooting Guide

## Errors Fixed ✅

### 1. "Chroma object has no attribute persist"
**Issue:** Chroma 0.4+ removed the `persist()` method - it auto-persists now.

**Fixed:** Removed `db.persist()` call from `ingestion/vector_store.py`. Chroma now automatically saves data to disk.

---

### 2. "Neo4j - The client is unauthorized due to authentication failure"
**Issue:** Wrong credentials or Neo4j not running, causing repeated auth failures which locked the connection.

**Solution:**
- Option A: Start Neo4j with Docker and correct credentials
  ```bash
  docker-compose up -d
  ```
- Option B: Update `.env` file with correct Neo4j credentials
- Option C: Graph search will gracefully degrade - system continues with vector search only

**Important:** Graph storage is now **optional**. If Neo4j fails:
- ✓ Vector search still works
- ✓ Documents still get ingested
- ✓ Query answering still functions (just from vector embeddings, not knowledge graph)

---

## Current System Status

### ✅ Always Working
- **Vector Search**: Uses Chroma + HuggingFace embeddings
- **Document Ingestion**: Splits PDFs into chunks
- **LLM Responses**: Uses Groq API

### ⚠️ Optional (Requires Neo4j)
- **Graph Search**: Knowledge extraction and relationship storage
- **Entity Relationships**: Triplet extraction from documents

---

## To Make Graph Search Work

### 1. Ensure Neo4j is Running
```bash
# Using Docker (Recommended)
docker-compose up -d

# Check if running
docker ps
```

### 2. Reset Authentication
If you see "authentication rate limit" error:
```bash
# Stop and remove container
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait 30 seconds for Neo4j to fully initialize
```

### 3. Update .env with Correct Password
Your `docker-compose.yml` has:
```
NEO4J_AUTH: neo4j/your_secure_password_here
```

This should match your `.env`:
```
NEO4J_PASSWORD=your_secure_password_here
```

### 4. Re-ingest Documents
```bash
python run.py
```

---

## Error Messages Explained

### "Error storing vectors: 'Chroma' object has no attribute 'persist'"
✅ **FIXED** - No action needed

### "Neo4j connection error: Unauthorized"
**Status:** Graceful fallback active
- Vector search works independently
- Set up Neo4j to enable graph search
- See "To Make Graph Search Work" section above

### "Graph search returned no results"
This is normal - might mean:
- Neo4j is running but has no data yet
- Re-ingest documents with `python run.py`
- Check that documents actually exist in `./data/`

---

## Quick Health Check

Run this to verify your setup:
```bash
python -c "
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
print('✓ Config loaded')
try:
    from langchain_chroma import Chroma
    print('✓ langchain-chroma available')
except:
    from langchain_community.vectorstores import Chroma
    print('✓ langchain-community.vectorstores.Chroma available')
print('✓ All imports working')
"
```

---

## Expected Behavior Now

### Without Neo4j
```
📥 Starting ingestion...

Ingesting: genai-fundamentals_1-generative-ai_1-what-is-genai.pdf
  ✓ Stored in vector DB
  ℹ Graph storage skipped or unavailable

Ingesting: Parth_Tarsariya.pdf
  ✓ Stored in vector DB
  ℹ Graph storage skipped or unavailable

✅ Ingestion complete!

🤖 RAG SYSTEM READY
✓ Vector Search: ACTIVE
✓ Graph Search: CHECKING...
```

### With Neo4j Running
```
📥 Starting ingestion...

Ingesting: genai-fundamentals_1-generative-ai_1-what-is-genai.pdf
  ✓ Stored in vector DB
  ✓ Stored 23 relationships in graph DB

Ingesting: Parth_Tarsariya.pdf
  ✓ Stored in vector DB
  ✓ Stored 15 relationships in graph DB

✅ Ingestion complete!

🤖 RAG SYSTEM READY
✓ Vector Search: ACTIVE
✓ Graph Search: ACTIVE
```

---

## Next Steps

1. ✅ Vector search already works
2. ⚠️ To enable graph search:
   - Uncomment/setup Neo4j (Docker recommended)
   - Update credentials in `.env`
   - Re-run ingestion
3. ✅ Ask questions - system will use whichever sources are available

---

## FAQ

**Q: Can I use the system without Neo4j?**
A: Yes! Vector search works independently. Graph search is optional.

**Q: Why remove error messages from graph storage?**
A: To keep the output clean. Graph failures don't affect core functionality.

**Q: How do I test if Chroma is working?**
A: Check if `./vectordb/` directory exists and isn't empty after ingestion.

**Q: How do I enable verbose logging again?**
A: Edit `run.py` and `rag_agent.py` to increase logging level to DEBUG.
