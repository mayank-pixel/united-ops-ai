from langchain.tools import tool

@tool
def chapter_router(query: str):
    """
    Vectorless RAG: Matches the user query to the specific FAA Handbook Chapter.
    Use this to identify which section of the manual to prioritize.
    """
    # This dictionary acts as our 'Vectorless' index
    ata_chapters = {
        "landing gear": "Chapter 13: Landing Gear Systems",
        "hydraulic": "Chapter 12: Hydraulic and Pneumatic Power Systems",
        "safety": "Chapter 13: FAA Regulations (General Handbook)",
        "instrument": "Chapter 10: Aircraft Instrument Systems"
    }
    
    query_lower = query.lower()
    for key, chapter in ata_chapters.items():
        if key in query_lower:
            return f"Structural Match Found: Focus search on {chapter}."
    
    return "No structural match. Proceed with semantic vector search."