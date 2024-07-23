import os
import requests
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils import extract_text_from_pdf
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = os.getenv("HF_API_URL")

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

pdf_text_storage = {}

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/upload/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_path = f"temp/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file.file.read())
        logging.info(f"File saved at {file_path}")

        pdf_text = extract_text_from_pdf(file_path)
        pdf_text_storage[file.filename] = pdf_text
        logging.info(f"Text extracted and stored for {file.filename}")

        return {"filename": file.filename}
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return {"error": str(e)}

@app.get("/query/", response_class=HTMLResponse)
async def query_page(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

@app.post("/query/")
async def query_pdf(filename: str = Form(...), query: str = Form(...)):
    pdf_text = pdf_text_storage.get(filename, "")

    if not pdf_text:
        return {"error": "File not found."}

    input_data = {
        "context": pdf_text,
        "question": query
    }
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=input_data
        )

        if response.status_code != 200:
            return {"error": f"Hugging Face API error: {response.json()}"}

        result = response.json()

        # Extract the answer from the API response
        if isinstance(result, dict) and "error" in result:
            return {"error": f"Hugging Face API error: {result['error']}"}
        elif isinstance(result, dict) and "answer" in result:
            answer = result['answer']
        else:
            return {"error": "Unexpected API response format"}

        return {"answer": answer.strip()}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}
