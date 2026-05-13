import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq

# Initialize LLM
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

llm = ChatGroq(
    api_key=groq_api_key,
    model="openai/gpt-oss-120b",
    temperature=0
)


def extract_triplets(text: str) -> str:
    """
    Extract entities and relationships as triplets from text
    
    Args:
        text: Input text to extract triplets from
    
    Returns:
        String containing triplets in format (entity1, relationship, entity2)
    """
    try:
        prompt = f"""You are an intelligent information extraction system.
Extract structured entity relationships from the given text to build a knowledge graph.

═══ RULE 1 — REAL NAMES ONLY ═══
Always use the ACTUAL name found in the document.
- Resume: use the candidate's real name (found in the header/title). NEVER write "Candidate", "Unnamed Candidate", "Person", or "Author".
- Article/Book: use the author's real name, not "Author".
- Last resort only if name truly cannot be found: "Unknown Person".

═══ RULE 2 — PROJECT EXTRACTION (most important for resumes) ═══
A PROJECT is identified by its TITLE (usually bold or on its own line, e.g. "Car Price Prediction", "Hybrid RAG System").
- Use ONLY the short project title as the project entity, NOT a task description or bullet point.
  ✓ CORRECT:  PersonName → worked on → Car Price Prediction
  ✗ WRONG:    PersonName → worked on → Integrated multi-source data for enhanced product insights
  ✗ WRONG:    PersonName → participated in → Improved ML model performance by 25%

- For each project, also extract:
  ProjectTitle → uses technology → TechName   (for each tool/library used in that project)
  ProjectTitle → achieved → AchievementFact    (specific measurable result, e.g. "8th place on Kaggle leaderboard")
  ProjectTitle → belongs to domain → DomainName  (e.g. "Machine Learning", "Web Development")

- Achievements and statistics (e.g. "25% improvement", "8th place") are properties of the PROJECT, not events the person "participated in".

═══ RULE 3 — RELATIONSHIPS TO EXTRACT ═══
Person relations:
  PersonName → has skill → SkillName
  PersonName → worked at → OrganizationName
  PersonName → studied at → OrganizationName
  PersonName → holds degree → DegreeName
  PersonName → held role → JobTitle
  PersonName → worked on → ProjectTitle        ← use project TITLE only
  PersonName → achieved → PersonalAchievement  ← only for person-level achievements (e.g. "CGPA 8.33")

Project relations:
  ProjectTitle → uses technology → TechName
  ProjectTitle → achieved → ResultFact
  ProjectTitle → belongs to domain → Domain

Other:
  OrganizationName → located in → Location
  TechName → used for → Task

═══ OUTPUT FORMAT ═══
Output ONLY relationship triples, one per line, nothing else:
Subject → Relation → Object

No bullet points, no numbering, no headers, no entity lists — ONLY triples.

Text:
{text}

Relationships:"""
        
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error extracting triplets: {str(e)}")
        return ""





# This is the recommended JSON-structured prompt for graph generation


#     You are an intelligent information extraction system.
#     Your task is to read any type of document — informative articles, research papers, books, or resumes —
#     and extract only the most meaningful entities and relationships for building a knowledge graph.
#     Skip generic filler content that does not contribute to understanding the document’s core knowledge.

#     Step 1: Read the entire document carefully and identify its type (book, article, resume, etc.).

#     Step 2: Extract key entities based on document type:
#     - For books / articles: Person, Organization, Concept, Location, Date, Event, Technology, Publication
#     - For resumes: Person, Skill, Job Title, Organization, Degree, Date, Project, Location

#     Step 3: Extract meaningful relationships such as:
#     - Person → authored → Publication
#     - Person → worked at → Organization
#     - Person → has skill → Skill
#     - Person → studied at → Organization
#     - Concept → is part of → Field
#     - Technology → used for → Task
#     - Event → occurred in → Location / Date

#     Step 4: Output in JSON format:
#     {
#     "entities": [
#         {"name": "Alan Turing", "type": "Person"},
#         {"name": "Computing Machinery and Intelligence", "type": "Publication"},
#         {"name": "Artificial Intelligence", "type": "Concept"},
#         {"name": "1950", "type": "Date"}
#     ],
#     "relationships": [
#         {"subject": "Alan Turing", "relation": "authored", "object": "Computing Machinery and Intelligence"},
#         {"subject": "Computing Machinery and Intelligence", "relation": "introduced", "object": "Artificial Intelligence"},
#         {"subject": "Alan Turing", "relation": "worked at", "object": "University of Manchester"}
#     ]
#     }
