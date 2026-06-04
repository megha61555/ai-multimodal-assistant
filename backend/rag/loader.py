from pypdf import PdfReader
from docx import Document

from PIL import Image
import pytesseract

import fitz  # PyMuPDF
import os

# =========================
# TESSERACT PATH
# =========================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# =========================
# PDF LOADER
# =========================

def load_pdf(path):

    text = ""

    try:

        reader = PdfReader(path)

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:

                text += extracted + "\n"

    except Exception as e:

        print("PDF TEXT ERROR:", e)

    # =========================
    # OCR FALLBACK
    # =========================

    if len(text.strip()) < 50:

        print("Using OCR for PDF...")

        try:

            doc = fitz.open(path)

            for page_num in range(len(doc)):

                page = doc.load_page(page_num)

                pix = page.get_pixmap()

                image_path = (
                    f"temp_page_{page_num}.png"
                )

                pix.save(image_path)

                image = Image.open(image_path)

                ocr_text = pytesseract.image_to_string(
                    image
                )

                text += ocr_text + "\n"

                os.remove(image_path)

        except Exception as e:

            print("OCR ERROR:", e)

    return text

# =========================
# DOCX LOADER
# =========================

def load_docx(path):

    doc = Document(path)

    text = ""

    for para in doc.paragraphs:

        text += para.text + "\n"

    return text

# =========================
# IMAGE LOADER
# =========================

def load_image(path):

    image = Image.open(path)

    text = pytesseract.image_to_string(
        image
    )

    return text

# =========================
# MAIN LOADER
# =========================

def load_document(path):

    lower_path = path.lower()

    if lower_path.endswith(".pdf"):

        return load_pdf(path)

    elif lower_path.endswith(".docx"):

        return load_docx(path)

    elif lower_path.endswith(

        (".png", ".jpg", ".jpeg")
    ):

        return load_image(path)

    return ""