from pydantic import BaseModel

class PDFUpload(BaseModel):
    filename: str

class UserQuery(BaseModel):
    query: str




