from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

def split_documents(text):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=300,

        chunk_overlap=80,

        separators=[

            "\n\n",

            "\n",

            ". ",

            " "
        ]
    )

    chunks = splitter.split_text(text)

    # REMOVE EMPTY CHUNKS

    cleaned_chunks = [

        chunk.strip()

        for chunk in chunks

        if len(chunk.strip()) > 30
    ]

    return cleaned_chunks