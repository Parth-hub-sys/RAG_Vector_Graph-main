from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable
import os
import logging

logger = logging.getLogger(__name__)

# # Read Neo4j configuration directly from environment variables
# NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
# NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = None


def get_driver():
    """Initialize and return a Neo4j driver using environment variables."""
    global driver
    if driver is None:
        try:
            uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            driver = GraphDatabase.driver(
                uri,
                auth=(user, password)
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Neo4j driver: {e}")
            driver = None
    return driver


def check_connection(timeout_seconds: int = 5) -> (bool, str):
    """Check connectivity to Neo4j. Returns (ok, message)."""
    try:
        d = get_driver()
        if d is None:
            return False, "driver-not-initialized"
        d.verify_connectivity()
        return True, "connected"
    except Exception as e:
        return False, str(e)

def graph_search(query: str):
    """Search graph database. Returns empty list if Neo4j is unavailable."""
    try:
        driver = get_driver()
        if driver is None:
            logger.warning("Neo4j is not available. Skipping graph search.")
            return []
        
        # Try multiple strategies to find relations for the query:
        # 1) match on left node name
        # 2) match on right node name
        # 3) search any property on either node (slower)

        queries = [
            (
                "MATCH (a)-[r]->(b)\n"
                "WHERE toLower(a.name) CONTAINS toLower($q)\n"
                "RETURN a.name AS a_name, type(r) AS rel, b.name AS b_name\n"
                "LIMIT 50"
            ),
            (
                "MATCH (a)-[r]->(b)\n"
                "WHERE toLower(b.name) CONTAINS toLower($q)\n"
                "RETURN a.name AS a_name, type(r) AS rel, b.name AS b_name\n"
                "LIMIT 50"
            ),
            (
                "MATCH (a)-[r]->(b)\n"
                "WHERE any(k IN keys(a) WHERE toLower(toString(a[k])) CONTAINS toLower($q))"
                " OR any(k IN keys(b) WHERE toLower(toString(b[k])) CONTAINS toLower($q))\n"
                "RETURN a.name AS a_name, type(r) AS rel, b.name AS b_name\n"
                "LIMIT 100"
            ),
        ]

        # First try the full query as-is
        relations = []
        with driver.session() as session:
            for cypher in queries:
                try:
                    result = session.run(cypher, q=query)
                except Exception as e:
                    logger.debug(f"Cypher query failed for full query: {e}")
                    continue

                for record in result:
                    try:
                        a = record.get("a_name")
                        r = record.get("rel")
                        b = record.get("b_name")
                        if a and r and b:
                            relations.append(f"{a} --[{r}]--> {b}")
                    except Exception:
                        continue

                if relations:
                    break

            # If no relations found for the full question, split into keywords and try each
            if not relations:
                # simple tokenization: split on spaces and punctuation
                import re
                tokens = [t.strip() for t in re.split(r"\W+", query) if t and len(t) > 2]
                # de-duplicate while preserving order
                seen = set()
                keywords = []
                for t in tokens:
                    tl = t.lower()
                    if tl not in seen:
                        seen.add(tl)
                        keywords.append(tl)

                for kw in keywords:
                    for cypher in queries:
                        try:
                            result = session.run(cypher, q=kw)
                        except Exception as e:
                            logger.debug(f"Cypher keyword query failed ({kw}): {e}")
                            continue

                        for record in result:
                            try:
                                a = record.get("a_name")
                                r = record.get("rel")
                                b = record.get("b_name")
                                if a and r and b:
                                    relations.append(f"{a} --[{r}]--> {b}")
                            except Exception:
                                continue

                    if relations:
                        break

        # Return unique relations preserving order
        unique = []
        seen = set()
        for rel in relations:
            if rel not in seen:
                seen.add(rel)
                unique.append(rel)

        return unique
    except (AuthError, ServiceUnavailable) as e:
        logger.warning(f"Neo4j connection error: {e}. Continuing without graph search.")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in graph_search: {e}")
        return []
