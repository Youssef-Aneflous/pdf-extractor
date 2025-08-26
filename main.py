import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import re
import unicodedata
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

def ocr_pdf(file_path: str) -> str:
    """Extract text from PDF using OCR (Arabic-aware)."""
    doc = fitz.open(file_path)
    full_text = []

    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img, lang="ara")
        full_text.append(text)

    return "\n".join(full_text)

def clean_arabic_text(text: str) -> str:
    """Clean extracted Arabic OCR text."""
    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # Remove diacritics
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]', '', text)

    # Remove Tatweel
    text = text.replace('\u0640', '')

    # Normalize Alef and Ya forms
    text = re.sub(r'[آأإٱ]', 'ا', text)
    text = text.replace('ى', 'ي')

    # Remove garbage (non-Arabic except punctuation and digits)
    text = re.sub(r'[^\u0600-\u06FF0-9\s.,؛:؟!()-]', ' ', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Ensure line breaks after sentence-ending punctuation
    text = re.sub(r'([\.؟!])\s*', r'\1\n', text)

    # Split into lines and remove empties
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    return "\n".join(lines)

@app.get("/")
async def root():
    return {"message": "PDF Extractor service is running"}

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    raw_text = ocr_pdf(temp_path)
    cleaned_text = clean_arabic_text(raw_text)

    return {"text": cleaned_text}
