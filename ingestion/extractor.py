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
Your task is to read any type of document — including informative articles, research papers, books, or resumes — and extract structured entities and relationships to build a knowledge graph.

Identify the following entities based on document type:

For informative documents / books / articles:
- Person (author, researcher, historical figure, expert)
- Organization (institution, company, government body, publisher)
- Concept / Topic (key ideas, theories, frameworks, subjects)
- Location (country, city, region, place)
- Date / Time Period (year, era, event date)
- Event (conference, discovery, publication, milestone)
- Technology / Tool (software, method, instrument)
- Work / Publication (book title, paper, article, report)

For resumes / CVs:
- Person (candidate name)
- Skill (programming language, framework, soft skill, certification)
- Job Title / Role (position held or applied for)
- Organization (employer, university, school)
- Degree / Qualification (education level, field of study)
- Date / Duration (employment period, graduation year)
- Project (key projects or achievements)
- Location (city, country of work or study)

Identify the following relationships based on context:
- Person → authored → Work / Publication
- Person → worked at → Organization
- Person → studied at → Organization
- Person → holds degree → Degree / Qualification
- Person → has skill → Skill
- Person → held role → Job Title
- Person → participated in → Event
- Concept → is part of → Topic / Field
- Organization → located in → Location
- Event → occurred in → Date / Location
- Technology → used for → Concept / Task
- Work → published by → Organization

Output format:
- Entities: List all extracted entities with their type labels
- Relationships: List all relationships as triples (Subject → Relation → Object)

Text: {text}

Output:"""
        
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
