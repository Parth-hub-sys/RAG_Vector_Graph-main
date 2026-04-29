import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# Read Neo4j configuration directly from environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
except Exception as e:
    print(f"Warning: Could not connect to Neo4j: {e}")
    print("Make sure Neo4j is running on your system")
    driver = None


import re


def clean_relationship(rel: str) -> str:
    """Convert relationship to Neo4j-safe format"""
    rel = rel.upper()
    rel = re.sub(r"[^A-Z0-9_]", "_", rel)  # remove special chars
    return rel


def store_graph(triplets: str) -> int:
    """Store knowledge triplets in Neo4j graph database.
    Returns gracefully if Neo4j is unavailable - graph is optional."""
    if not driver:
        # Graph storage is optional - system works with vector search alone
        return 0

    stored_count = 0

    try:
        with driver.session() as session:
            for line in triplets.split("\n"):
                line = line.strip()
                if not line:
                    continue

                try:
                    # Remove bullet point if present
                    if line.startswith("- "):
                        line = line[2:]
                    elif line.startswith("* "):
                        line = line[2:]

                    parts = []
                    # 1. Try original (Entity, Relation, Entity) format
                    if line.startswith("("):
                        cleaned = line.strip("()")
                        parts = [p.strip() for p in cleaned.split(",", 2)]
                    # 2. Try Subject → Relation → Object format from new prompt
                    elif " → " in line:
                        parts = [p.strip() for p in line.split(" → ", 2)]
                    elif " -> " in line:
                        parts = [p.strip() for p in line.split(" -> ", 2)]
                    elif " - " in line and line.count(" - ") >= 2:
                        parts = [p.strip() for p in line.split(" - ", 2)]

                    if len(parts) < 3:
                        continue

                    entity1 = parts[0].strip("'\"")
                    relationship = clean_relationship(parts[1].strip("'\""))
                    entity2 = parts[2].strip("'\"")

                    cypher = f"""
MERGE (a:Entity {{name: $e1}})
MERGE (b:Entity {{name: $e2}})
MERGE (a)-[r:{relationship}]->(b)
"""

                    session.run(cypher, e1=entity1, e2=entity2)
                    stored_count += 1

                except Exception:
                    # Skip failed triplets, continue with others
                    pass

        return stored_count

    except Exception:
        # Graph storage failure doesn't block ingestion
        # Vector search will still work
        return 0


def close_driver():
    """Close the Neo4j driver connection"""
    if driver:
        driver.close()

