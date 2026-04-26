import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def build_knowledge_base():
    # 1. Paths
    PDF_PATH = "data/raw_pdfs"
    INDEX_PATH = "data/faiss_index"
    
    print(f"📂 Scanning for manuals in {PDF_PATH}...")
    
    # 2. Load
    loader = PyPDFDirectoryLoader(PDF_PATH)
    documents = loader.load()
    print(f"📄 Loaded {len(documents)} pages.")

    # 3. Smart Chunking
    # For 1000+ pages, we use a larger chunk with overlap to keep context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️ Created {len(chunks)} technical chunks.")

    # 4. Embed (The "Heavy" part)
    print("🧠 Generating Vector Index (this might take a few minutes for 1000+ pages)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # 5. Save to Disk
    os.makedirs(INDEX_PATH, exist_ok=True)
    vectorstore.save_local(INDEX_PATH)
    print(f"✅ SUCCESS: Knowledge base saved to {INDEX_PATH}")

if __name__ == "__main__":
    build_knowledge_base()