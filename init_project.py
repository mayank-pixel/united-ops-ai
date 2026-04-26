import os

# Define the folder and file structure
structure = {
    "data/raw_pdfs": [],
    "data/processed_json": [],
    "data/faiss_index": [],
    "src/agents": ["__init__.py", "researcher.py", "safety_auditor.py", "analyst.py"],
    "src/tools": ["__init__.py", "vector_tool.py", "structural_tool.py"],
    "src/graph": ["__init__.py", "state.py", "nodes.py", "workflow.py"],
    "src/simulator": ["__init__.py", "cockpit_chat.py"],
    "": ["app.py", ".env", "requirements.txt", "README.md"]
}

def create_structure():
    for folder, files in structure.items():
        # Create directories
        if folder:
            os.makedirs(folder, exist_ok=True)
            print(f"📁 Created folder: {folder}")
        
        # Create files
        for file in files:
            file_path = os.path.join(folder, file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    # Pre-fill README with the project vision
                    if file == "README.md":
                        f.write("# United Airlines: Technical Safety Agent\n\nAgentic RAG with LangGraph & CrewAI.")
                    pass
                print(f"  📄 Created file: {file_path}")

if __name__ == "__main__":
    create_structure()
    print("\n✅ Project structure initialized! Ready for referral-grade engineering.")