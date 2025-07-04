# app/tools/hr_tools.py

from app.services.vectorstore_service import VectorStore
from typing import List
from datetime import datetime

# Load and cache the vector store at startup
_vectorstore = VectorStore()._init_vectorstore()


def read_policy_documents(query: str, matched_category: str) -> str:
    """
    Reads HR policy documents and returns relevant context based on user query and category.
    """

    print('matched_category>>>> ',matched_category)
    retriever = _vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2, "filter": {"category": matched_category}})
    relevant_docs = retriever.invoke(query)
    # return "\n\n".join(doc.page_content for doc in relevant_docs) if relevant_docs else 'No relevant documents found for your query.'
    return "\n\n".join(doc.page_content for doc in relevant_docs) if relevant_docs else None


def get_all_categories_from_index() -> List[str]:
    """
    Returns all unique document categories from the indexed policy documents.
    """
    categories = set()
    for doc in _vectorstore.docstore._dict.values():
        category = doc.metadata.get("category")
        if category:
            categories.add(category.strip())
    return list(categories)

def get_current_budget(month: str = "") -> str:
    """
    Retrieves the budget for the specified month. If not provided, uses the current month.
    """
    if not month:
        month = datetime.now().strftime("%B")  # e.g., "May"
    return f"The budget for {month} is $1500. TERMINATE"