from pydantic import BaseModel
from fastapi import UploadFile

class SaveDiaryRequestDTO(BaseModel):
    yyyymmdd: str
    content: str
    images: list[UploadFile]

class SaveDiaryResponseDTO(BaseModel):
    id: int
    yyyymmdd: str
    content: str
    image_urls: list[str]

class GetDiaryResponseDTO(BaseModel):
    id: int
    content: str
    image_urls: list[str]
