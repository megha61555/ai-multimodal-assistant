import ollama

# =========================
# TEXT MODEL
# =========================

TEXT_MODEL = "phi3"

# =========================
# IMAGE MODELS
# =========================

VISION_MODEL_HEAVY = "llava"

VISION_MODEL_LIGHT = "moondream"

# =========================
# TEXT CHAT
# =========================

def ask_llama(prompt):

    response = ollama.chat(

        model=TEXT_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

# =========================
# FAST IMAGE MODEL
# =========================

def ask_image_fast(image_path, prompt):

    response = ollama.chat(

        model=VISION_MODEL_LIGHT,

        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }
        ]
    )

    return response["message"]["content"]

# =========================
# DETAILED IMAGE MODEL
# =========================

def ask_image_detailed(image_path, prompt):

    response = ollama.chat(

        model=VISION_MODEL_HEAVY,

        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }
        ]
    )

    return response["message"]["content"]