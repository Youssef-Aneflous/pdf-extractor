from pdfminer.high_level import extract_text
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pdfplumber
import re

app = FastAPI(title="PDF Text Extractor")

def clean_text(text: str) -> str:
    """Clean extracted text."""
    if not text:
        return ""
    # Replace form feed (page breaks) with newline
    text = text.replace("\x0c", "\n")
    # Replace multiple newlines with a single newline
    text = re.sub(r"\n+", "\n", text)
    # Strip leading/trailing whitespace
    return text.strip()
    
@app.get("/")
async def root():
    return {"message": "PDF Extractor service is running"}
 
@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read the PDF
        with pdfplumber.open(file.file) as pdf:
            text_pages = [page.extract_text() for page in pdf.pages]
        
        # Combine all pages and clean
        full_text = "\n".join(filter(None, text_pages))
        cleaned_text = clean_text(full_text)

        return JSONResponse(content={"text": cleaned_text})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting PDF: {str(e)}")
