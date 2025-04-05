from pydantic import BaseModel
import uuid

class SaveDiaryRequestDTO(BaseModel):
    yyyymmdd: str
    content: str

class SaveDiaryResponseDTO(BaseModel):
    id: uuid.UUID
    yyyymmdd: str
    content: str
    image_ids: list[uuid.UUID]

class GetDiaryResponseDTO(BaseModel):
    id: uuid.UUID
    yyyymmdd: str
    content: str
    image_ids: list[uuid.UUID]
