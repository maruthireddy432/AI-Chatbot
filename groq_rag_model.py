
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangChain Imports
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


class GroqRAGModel:
    def __init__(
        self,
        groq_api_key: str = None,
        model_name: str = "groq/compound",  # Using a standard Groq model
        persist_directory: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """
        Initialize the RAG model using a prebuilt Chroma DB and Groq LLM.
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError(
                "Groq API key is required. Set GROQ_API_KEY in .env or pass it as groq_api_key"
            )

        self.model_name = model_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.vectordb = None
        self.qa_chain = None

        # Initialize pipeline
        self.load_vector_db()
        self.create_qa_chain()

    def load_vector_db(self):
        """Load existing Chroma vector database from disk."""
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(
                f"Chroma DB directory not found at {self.persist_directory}."
            )

        print("[INFO] Loading existing Chroma DB...")
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        self.vectordb = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings,
        )
        print("[SUCCESS] Vector DB loaded successfully.")

    def create_qa_chain(self):
        """Create a RetrievalQA pipeline using Groq LLM with a custom JSON prompt."""
        if not self.vectordb:
            raise ValueError("Vector DB not loaded. Load it before creating QA chain.")

        retriever = self.vectordb.as_retriever(search_kwargs={"k": 3})
        
        # This is the key change: A custom prompt template
        prompt_template = """Use the following pieces of context to answer the user's question.
        You absolutely must respond in a valid JSON format. Do not include any text, reasoning, or preamble outside of the JSON structure.

        The JSON object must follow this structure:
        [
            {{"type": "header", "content": "Main Title Related to the Question"}},
            {{
                "type": "section", 
                "title": "Category Title (e.g., Credit & Financing)", 
                "items": [
                    {{"scheme": "Name of the Scheme", "description": "A brief description of the scheme based on the context."}}
                ]
            }}
        ]

        Context: {context}

        Question: {question}

        Helpful Answer (in valid JSON format):
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        llm = ChatGroq(
            api_key=self.groq_api_key,
            model=self.model_name,
            # Force the model to output a JSON object
            response_format={"type": "json_object"}
        )

        chain_type_kwargs = {"prompt": PROMPT}
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs=chain_type_kwargs,
        )
        print(f"[READY] Groq QA chain initialized with model: {self.model_name}")

    def ask(self, query: str) -> dict | list | str:
        """
        Ask a question and get an LLM-generated answer.
        The answer is expected to be a parsed JSON object (dict or list).
        """
        if not self.qa_chain:
            self.create_qa_chain()

        try:
            # Use .invoke() which is the standard LangChain interface
            result = self.qa_chain.invoke({"query": query})
        except Exception as e:
            print(f"[ERROR] Failed to get response from Groq: {e}")
            return "Error: Could not get answer at this time."

        # The 'result' key now contains the parsed dictionary/list from the JSON output
        answer = result.get("result")
        return answer