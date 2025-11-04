
import os
import glob
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --------------- CONFIGURATION --------------- #
# ✅ Use raw string or forward slashes for paths to avoid escape issues on Windows
PDF_FOLDER = r"D:\Live projects\AI Chatbot\data"
CHROMA_DB_PATH = r"./chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# --------------- EXTRACT TEXT FROM PDF --------------- #
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract plain text from a PDF file using PyMuPDF.
    """
    text_parts = []
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_parts.append(page.get_text("text"))
    except Exception as e:
        print(f"[ERROR] Failed to read {pdf_path}: {e}")
        return ""
    return "\n".join(text_parts)


def load_pdfs_from_folder(folder: str):
    """
    Return all PDF file paths from a folder.
    """
    pdf_files = sorted(glob.glob(os.path.join(folder, "*.pdf")))
    if not pdf_files:
        print(f"[WARNING] No PDFs found in folder: {folder}")
    return pdf_files


# --------------- CHUNKING + VECTOR DB CREATION --------------- #
def create_vector_db_from_pdfs():
    """
    Read PDFs, extract text, create embeddings, and save as a Chroma DB.
    """
    pdf_files = load_pdfs_from_folder(PDF_FOLDER)
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in folder: {PDF_FOLDER}")

    print(f"[INFO] Found {len(pdf_files)} PDF(s). Extracting text...")
    all_texts = []
    for pdf_path in pdf_files:
        print(f"   → Extracting from: {os.path.basename(pdf_path)}")
        text = extract_text_from_pdf(pdf_path)
        if text.strip():
            all_texts.append(text)
        else:
            print(f"   ⚠️ Warning: {os.path.basename(pdf_path)} seems empty or unreadable.")

    if not all_texts:
        raise ValueError("No valid text extracted from PDFs. Please check input files.")

    combined_text = "\n\n".join(all_texts)

    print("[INFO] Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_text(combined_text)
    print(f"[INFO] Created {len(chunks)} chunks.")

    print("[INFO] Creating embeddings and saving Chroma database...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    # Initialize Chroma DB; if directory exists, it will load it
    vectordb = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)

    # Add texts only if DB is empty to avoid duplication
    if len(vectordb._collection.get()['ids']) == 0:  # Check existing IDs
        ids = [str(i) for i in range(len(chunks))]
        vectordb.add_texts(chunks, ids=ids)
        vectordb.persist()
        print(f"[SUCCESS] Chroma DB successfully saved at: {os.path.abspath(CHROMA_DB_PATH)}")
    else:
        print(f"[INFO] Chroma DB already contains data. Skipping adding texts.")


if __name__ == "__main__":
    create_vector_db_from_pdfs()
