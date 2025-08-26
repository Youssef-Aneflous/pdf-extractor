from pdfminer.high_level import extract_text
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pdfplumber
import re
import unicodedata

app = FastAPI(title="PDF Text Extractor")



def clean_text(text: str) -> str:
    """Clean extracted Arabic text."""
    if not text:
        return ""

    # Normalize Unicode
    text = unicodedata.normalize("NFC", text)

    # Replace form feed (page breaks) with newline
    text = text.replace("\x0c", "\n")

    # Remove Arabic diacritics
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]', '', text)

    # Remove Tatweel
    text = text.replace('\u0640', '')

    # Normalize Alef forms and Ya
    text = re.sub(r'[آأإٱ]', 'ا', text)
    text = text.replace('ى', 'ي')

    # Remove garbage (non-Arabic letters, but keep digits, punctuation, and spaces)
    text = re.sub(r'[^\u0600-\u06FF0-9\s.,؛:؟!()-]', ' ', text)

    # Normalize multiple spaces to single
    text = re.sub(r'\s+', ' ', text)

    # Split into lines, keep meaningful ones
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Optional: put one line per sentence using common sentence punctuation
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'([\.؟!])\s*', r'\1\n', line)
        cleaned_lines.extend([l.strip() for l in line.split("\n") if l.strip()])

    return "\n".join(cleaned_lines)


    
@app.get("/")
async def root():
    return {"message": "PDF Extractor service is running"}
 
@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    try:
        # Read the PDF
        with pdfplumber.open(file.file) as pdf:
            text_pages = [page.extract_text() for page in pdf.pages]
        
        full_text = "\n".join(filter(None, text_pages))
        cleaned_text = clean_text(full_text)

        return {"text": cleaned_text}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot process file: {str(e)}")

