from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

import os
import re

from backend.llm.ollama_llm import (
    ask_llama,
    ask_image_fast,
    ask_image_detailed
)

from backend.rag.loader import load_document
from backend.rag.splitter import split_documents
from backend.rag.vectorstore import create_vectorstore
from backend.rag.retriever import retrieve_docs

from backend.tools.web_search import search_web

app = Flask(__name__)

CORS(app)

# ==========================================
# MEMORY
# ==========================================

chat_history = []

user_memory = {
    "name": None
}

last_uploaded_image = None

last_related_questions = []

# ==========================================
# FORMAT RESPONSE
# ==========================================

def format_response(answer, questions):

    return f"""
Answer:

{answer}

You can also ask:

1. {questions[0]}

2. {questions[1]}

3. {questions[2]}
"""

# ==========================================
# RELATED QUESTIONS
# ==========================================

def generate_pdf_related_questions(question):

    return [

        f"What are the important points about {question}?",

        f"Can you summarize the section related to {question}?",

        f"Explain {question} in simple words?"
    ]


def generate_image_related_questions(question):

    return [

        "What objects are visible in the image?",

        "Can you explain the image in detail?",

        "What is the main theme of the image?"
    ]


def generate_web_related_questions(question):

    return [

        f"What is the latest update about {question}?",

        f"Why is {question} trending today?",

        f"What are experts saying about {question}?"
    ]


def generate_general_related_questions(question):

    return [

        f"Can you explain more about {question}?",

        f"Can you give another example related to {question}?",

        f"What are some interesting facts about {question}?"
    ]

# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")

# ==========================================
# CHAT
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    global last_uploaded_image
    global last_related_questions

    data = request.get_json()

    user_message = data.get(
        "message",
        ""
    ).strip()

    lower_msg = user_message.lower()

    # ==========================================
    # FOLLOW-UP QUESTIONS
    # ==========================================

    if lower_msg in ["1", "2", "3"]:

        try:

            selected_index = (
                int(lower_msg) - 1
            )

            if (
                0 <= selected_index
                < len(last_related_questions)
            ):

                selected_question = (
                    last_related_questions[
                        selected_index
                    ]
                )

                user_message = (
                    selected_question
                )

                lower_msg = (
                    selected_question.lower()
                )

                print(
                    "FOLLOW-UP:",
                    user_message
                )

            else:

                return jsonify({

                    "response":
                    "No related question found."
                })

        except Exception as e:

            return jsonify({

                "response":
                f"Follow-up Error: {str(e)}"
            })

    # ==========================================
    # GREETINGS
    # ==========================================

    greetings = {

        "hi":
        "Hello 👋 What can I do for you?",

        "hello":
        "Hi 😊 What can I help you with?",

        "hey":
        "Hey 👋 How can I assist you?",

        "gm":
        "Good Morning ☀️",

        "good morning":
        "Good Morning ☀️"
    }

    bye_messages = {

        "bye":
        "Bye 👋 Have a nice day!",

        "good night":
        "Good night 🌙"
    }

    if lower_msg in greetings:

        return jsonify({

            "response":
            greetings[lower_msg]
        })

    if lower_msg in bye_messages:

        return jsonify({

            "response":
            bye_messages[lower_msg]
        })

    # ==========================================
    # NAME MEMORY
    # ==========================================

    name_patterns = [

        r"my name is (.+)",

        r"i am (.+)",

        r"i'm (.+)"
    ]

    for pattern in name_patterns:

        match = re.search(
            pattern,
            lower_msg
        )

        if match:

            extracted_name = (
                match.group(1)
                .strip()
                .title()
            )

            user_memory["name"] = (
                extracted_name
            )

            return jsonify({

                "response":
                f"Nice to meet you {extracted_name} 😊"
            })

    # ==========================================
    # WEB SEARCH
    # ==========================================

    web_keywords = [

        "today",
        "latest",
        "current",
        "news",
        "weather",
        "live",
        "recent",
        "score",
        "gold",
        "silver",
        "price",
        "stock",
        "rate"
    ]

    if any(
        word in lower_msg
        for word in web_keywords
    ):

        try:

            web_results = search_web(
                user_message
            )

            if not web_results:

                return jsonify({

                    "response":
                    "Could not fetch live web results."
                })

            web_context = ""

            for result in web_results:

                web_context += f"""

Title:
{result['title']}

Info:
{result['body']}

"""

            web_prompt = f"""

You are a helpful AI assistant.

Use ONLY the web results.

RULES:

1. Keep answers short.
2. Use simple English.
3. Be accurate.

WEB RESULTS:
{web_context}

QUESTION:
{user_message}

"""

            web_answer = ask_llama(
                web_prompt
            )

            last_related_questions = (
                generate_web_related_questions(
                    user_message
                )
            )

            final_response = (
                format_response(

                    web_answer,

                    last_related_questions
                )
            )

            return jsonify({

                "response":
                final_response
            })

        except Exception as e:

            return jsonify({

                "response":
                f"Web Search Error: {str(e)}"
            })

    # ==========================================
    # IMAGE UNDERSTANDING
    # ==========================================

    image_keywords = [

        "image",
        "photo",
        "picture",
        "describe image",
        "describe this image",
        "what is in the image",
        "explain image",
        "analyze image",
        "explain the above image",
        "pic"
    ]

    if any(
        keyword in lower_msg
        for keyword in image_keywords
    ):

        if last_uploaded_image:

            try:

                if any(
                    word in lower_msg
                    for word in [

                        "detail",
                        "deep",
                        "analyze"
                    ]
                ):

                    image_answer = (
                        ask_image_detailed(

                            last_uploaded_image,

                            user_message
                        )
                    )

                else:

                    image_answer = (
                        ask_image_fast(

                            last_uploaded_image,

                            user_message
                        )
                    )

                last_related_questions = (
                    generate_image_related_questions(
                        user_message
                    )
                )

                final_response = (
                    format_response(

                        image_answer,

                        last_related_questions
                    )
                )

                return jsonify({

                    "response":
                    final_response
                })

            except Exception as e:

                return jsonify({

                    "response":
                    f"Image Error: {str(e)}"
                })

    # ==========================================
    # GENERAL CHAT
    # ==========================================

    general_chat_keywords = [

        "poem",
        "poetry",
        "story",
        "joke",
        "motivate",
        "quote",
        "song",
        "essay",
        "speech",
        "tell me",
        "write",
        "create",
        "generate",
        "funny",
        "love",
        "birthday",
        "friendship"
    ]

    if any(
        word in lower_msg
        for word in general_chat_keywords
    ):

        try:

            general_prompt = f"""

You are a friendly AI assistant.

RULES:

1. Keep answers short.
2. Use simple English.
3. Be creative.
4. Be friendly.

QUESTION:
{user_message}

"""

            general_answer = ask_llama(
                general_prompt
            )

            last_related_questions = (
                generate_general_related_questions(
                    user_message
                )
            )

            final_response = (
                format_response(

                    general_answer,

                    last_related_questions
                )
            )

            return jsonify({

                "response":
                final_response
            })

        except Exception as e:

            return jsonify({

                "response":
                f"General Chat Error: {str(e)}"
            })

    # ==========================================
    # DOCUMENT RETRIEVAL
    # ==========================================

    context = ""

    try:

        docs = retrieve_docs(
            user_message
        )

        for doc in docs:

            try:

                context += (
                    doc.page_content
                    + "\n"
                )

            except:

                context += (
                    str(doc)
                    + "\n"
                )

    except Exception as e:

        print(
            "Retriever Error:",
            e
        )

    # ==========================================
    # FALLBACK GENERAL CHAT
    # ==========================================

    if not context.strip():

        fallback_prompt = f"""

You are a friendly AI assistant.

QUESTION:
{user_message}

Keep answers:
- short
- simple
- helpful

"""

        fallback_answer = ask_llama(
            fallback_prompt
        )

        last_related_questions = (
            generate_general_related_questions(
                user_message
            )
        )

        final_response = (
            format_response(

                fallback_answer,

                last_related_questions
            )
        )

        return jsonify({

            "response":
            final_response
        })

    # ==========================================
    # PDF PROMPT
    # ==========================================

    user_name = user_memory.get(
        "name"
    )

    final_prompt = f"""

You are a document assistant.

Answer ONLY from document context.

RULES:

1. Do NOT hallucinate.
2. Keep answers short.
3. Use simple English.
4. If answer not found say:
"I could not find this in the document."

USER:
{user_name}

DOCUMENT:
{context}

QUESTION:
{user_message}

"""

    try:

        pdf_answer = ask_llama(
            final_prompt
        )

    except Exception as e:

        pdf_answer = (
            f"LLM Error: {str(e)}"
        )

    last_related_questions = (
        generate_pdf_related_questions(
            user_message
        )
    )

    final_response = (
        format_response(

            pdf_answer,

            last_related_questions
        )
    )

    chat_history.append({

        "user":
        user_message,

        "bot":
        final_response
    })

    return jsonify({

        "response":
        final_response,

        "history":
        chat_history
    })

# ==========================================
# FILE UPLOAD
# ==========================================

@app.route("/upload", methods=["POST"])
def upload_file():

    global last_uploaded_image

    try:

        if "file" not in request.files:

            return jsonify({

                "message":
                "No file uploaded"
            })

        file = request.files["file"]

        if file.filename == "":

            return jsonify({

                "message":
                "No selected file"
            })

        upload_folder = "uploads"

        os.makedirs(

            upload_folder,

            exist_ok=True
        )

        filepath = os.path.join(

            upload_folder,

            file.filename
        )

        file.save(filepath)

        # IMAGE

        if filepath.lower().endswith(

            (
                ".png",
                ".jpg",
                ".jpeg"
            )
        ):

            last_uploaded_image = (
                filepath
            )

        # DOCUMENT

        document_text = (
            load_document(filepath)
        )

        if not document_text:

            return jsonify({

                "message":
                "Could not read file"
            })

        chunks = split_documents(
            document_text
        )

        create_vectorstore(
            chunks
        )

        return jsonify({

            "message":
            f"{file.filename} uploaded successfully"
        })

    except Exception as e:

        return jsonify({

            "message":
            f"Upload Error: {str(e)}"
        })

# ==========================================
# HISTORY
# ==========================================

@app.route("/history")
def history():

    return jsonify({

        "history":
        chat_history
    })

# ==========================================
# CLEAR CHAT
# ==========================================

@app.route("/clear", methods=["POST"])
def clear_chat():

    global chat_history
    global last_related_questions

    chat_history = []

    last_related_questions = []

    return jsonify({

        "message":
        "Chat history cleared"
    })

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    app.run(

        debug=True,

        use_reloader=False,

        host="0.0.0.0",

        port=5000
    )