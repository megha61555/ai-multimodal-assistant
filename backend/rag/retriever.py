from langchain_community.vectorstores import Chroma

from backend.rag.embeddings import (
    get_embeddings
)

def retrieve_docs(query):

    embeddings = get_embeddings()

    vectorstore = Chroma(

        persist_directory="vector_db",

        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(

        search_type="similarity",

        search_kwargs={

            "k": 3
        }
    )

    docs = retriever.invoke(query)

    # FILTER VERY SMALL CHUNKS

    filtered_docs = []

    for doc in docs:

        if len(doc.page_content.strip()) > 40:

            filtered_docs.append(doc)

    return filtered_docs