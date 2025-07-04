import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.document_loader_service import DocumentLoader
from app.app_generalize_settings import GEMINI_API_KEY


# === VectorStore ===
class VectorStore:

    def _init_vectorstore(self, force_refresh=False):
        db_path = "documents_cache/faiss_index"
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GEMINI_API_KEY
        )

        if os.path.exists(db_path) and not force_refresh:
            return FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)

        existing_store = None
        if os.path.exists(db_path):
            existing_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)

        loader = DocumentLoader()
        new_docs = loader._load_documents()

        if not new_docs:
            return existing_store or FAISS.from_documents([], embeddings)

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        new_chunks = splitter.split_documents(new_docs)
        new_store = FAISS.from_documents(new_chunks, embeddings)

        if existing_store:
            existing_store.merge_from(new_store)
            existing_store.save_local(db_path)
            return existing_store

        os.makedirs("documents_cache", exist_ok=True)
        new_store.save_local(db_path)
        return new_store

    def _get_all_categories_from_index(vectorstore):
        """Extracts all unique categories from indexed documents."""
        categories = set()
        for doc in vectorstore.docstore._dict.values():
            category = doc.metadata.get("category")
            if category:
                categories.add(category.strip())
        return list(categories)