import os
import glob
import fitz
from typing import List, Optional
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

load_dotenv()

# Optional Groq LLM integration
try:
    from langchain_groq import ChatGroq
    USE_LANGCHAIN_GROQ = True
except ImportError:
    USE_LANGCHAIN_GROQ = False
    ChatGroq = None


class PDFGroqRAG:
    """
    End-to-End RAG pipeline: PDFs -> Chroma embeddings -> Groq LLM QA.
    """

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        model_name: str = "llama-3.1-70b-versatile",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.groq_api_key = (groq_api_key or os.getenv("GROQ_API_KEY", "")).strip()
        if not self.groq_api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY in .env or pass directly.")

        self.model_name = model_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.vectordb = None
        self.qa_chain = None

    # ---------------- TEXT EXTRACTION ---------------- #
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text_parts = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_parts.append(page.get_text("text"))
        return "\n".join(text_parts)

    def load_pdfs_from_folder(self, folder: str) -> List[str]:
        return sorted(glob.glob(os.path.join(folder, "*.pdf")))

    # ---------------- CHUNKING ---------------- #
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_text(text)

    # ---------------- EMBEDDINGS + VECTOR DB ---------------- #
    def create_vector_db(self, chunks: List[str]):
        os.makedirs(self.persist_directory, exist_ok=True)
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=embeddings)
        vectordb.add_texts(chunks, ids=[str(i) for i in range(len(chunks))])
        vectordb.persist()
        self.vectordb = vectordb
        print(f"[SUCCESS] Vector DB created at: {self.persist_directory}")
        return vectordb

    def load_existing_vector_db(self):
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Chroma DB not found at '{self.persist_directory}'")
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        self.vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=embeddings)
        print("[INFO] Existing vector DB loaded.")
        return self.vectordb

    # ---------------- QA CHAIN ---------------- #
    def create_qa_chain(self):
        if not self.vectordb:
            raise ValueError("Vector DB not found. Run ingest_pdfs() or load_existing_vector_db() first.")
        if not USE_LANGCHAIN_GROQ:
            raise ImportError("langchain-groq not installed. Install via: pip install langchain-groq")

        retriever = self.vectordb.as_retriever(search_kwargs={"k": 3})
        llm = ChatGroq(api_key=self.groq_api_key, model=self.model_name)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )
        print(f"[READY] QA chain initialized with Groq model '{self.model_name}'")
        return self.qa_chain

    # ---------------- MAIN PIPELINE ---------------- #
    def ingest_pdfs(self, pdf_folder: str = "./data", chunk_size: int = 1000, chunk_overlap: int = 200):
        pdf_files = self.load_pdfs_from_folder(pdf_folder)
        if not pdf_files:
            raise FileNotFoundError(f"No PDFs found in folder: {pdf_folder}")

        print(f"[INFO] Found {len(pdf_files)} PDF(s). Extracting text...")
        all_texts = [self.extract_text_from_pdf(p) for p in pdf_files]
        combined_text = "\n\n".join(all_texts)
        chunks = self.chunk_text(combined_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        print(f"[INFO] Created {len(chunks)} chunks.")

        self.create_vector_db(chunks)
        self.create_qa_chain()
        print("[READY] RAG pipeline initialized.")

    def ask(self, query: str) -> str:
        if not self.qa_chain:
            if self.vectordb is None:
                self.load_existing_vector_db()
            self.create_qa_chain()
        try:
            result = self.qa_chain({"query": query})
            return (result.get("result") or result.get("answer") or "").strip()
        except Exception as e:
            print(f"[ERROR] Groq QA failed: {e}")
            return "Error: Could not get answer at this time."

    def search_sources(self, query: str, top_k: int = 3) -> List[str]:
        if not self.vectordb:
            self.load_existing_vector_db()
        retriever = self.vectordb.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.get_relevant_documents(query)
        return [d.page_content for d in docs]


# ---------------- Example Run ---------------- #
if __name__ == "__main__":
    rag = PDFGroqRAG(groq_api_key=os.getenv("GROQ_API_KEY"))
    rag.ingest_pdfs(pdf_folder=r"Live projects\AI Chatbot\data")
    question = "Summarize the scheme highlights from the report."
    print("\nQ:", question)
    print("A:", rag.ask(question))
