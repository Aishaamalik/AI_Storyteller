from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

class RAGRetriever:
    def __init__(self, pdf_path="story.pdf", embedding_model="all-MiniLM-L6-v2"):
        self.pdf_path = pdf_path
        self.embedding_model = embedding_model
        self.vectorstore = None
        self._load_and_index()

    def _load_and_index(self):
        if not os.path.exists(self.pdf_path):
            print(f"Warning: {self.pdf_path} not found. RAG will not work.")
            return

        # Load PDF
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)

        # Create embeddings
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

        # Build FAISS index
        self.vectorstore = FAISS.from_documents(docs, embeddings)

    def retrieve(self, query, k=3):
        if self.vectorstore is None:
            return []
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
