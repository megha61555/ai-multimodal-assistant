from langchain_community.vectorstores import Chroma

from backend.rag.embeddings import (
    get_embeddings
)

def create_vectorstore(chunks):

    embeddings = get_embeddings()

    vectorstore = Chroma.from_texts(

        texts=chunks,

        embedding=embeddings,

        persist_directory="vector_db"
    )

    vectorstore.persist()

    return vectorstore