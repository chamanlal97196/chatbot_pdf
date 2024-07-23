from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_pdf():
    with open("sample.pdf", "rb") as f:
        response = client.post("/upload/", files={"file": ("sample.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert "filename" in response.json()

def test_query_pdf():
    query = {"query": "What is the main topic of the PDF?", "filename": "sample.pdf"}
    response = client.post("/query/", data=query)
    assert response.status_code == 200
    assert "answer" in response.json()
