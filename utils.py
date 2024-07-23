from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_file_path: str) -> str:
    reader = PdfReader(pdf_file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
