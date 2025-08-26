from fastapi import FastAPI, UploadFile, File
from pdfminer.high_level import extract_text
import tempfile

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "PDF Extractor service is running"}
    
@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(await file.read())
        tmp_file_path = tmp_file.name

    # Extract text
    try:
        text = extract_text(tmp_file_path)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}
