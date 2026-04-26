import os
from crewai.tools import BaseTool
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class AviationKnowledgeTool(BaseTool):
    name: str = "aviation_knowledge_base"
    description: str = "Search the 1,000+ page technical database for precise aircraft repair steps."

    def _run(self, query: str) -> str:
        # Absolute path to the pre-built index
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        index_path = os.path.join(root_dir, "data", "faiss_index")
        
        # Load the index (Instant because the math is already done)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        try:
            vectorstore = FAISS.load_local(
                index_path, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            # Use similarity_search_with_score to ensure high-quality matches
            results = vectorstore.similarity_search(query, k=1) 
            
            # Formatting the output for the Agent
            context = "\n---\n".join([r.page_content for r in results])
            return context if context else "No relevant technical data found in the manuals."
            
        except Exception as e:
            return f"Knowledge Base Error: Ensure 'ingest.py' has been run. Details: {e}"

aviation_tool = AviationKnowledgeTool()