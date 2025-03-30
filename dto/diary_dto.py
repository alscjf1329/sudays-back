from pydantic import BaseModel

class DiarySaveRequestDTO(BaseModel):
    yyyymmdd: str
    title: str
    content: str

class DiarySaveResponseDTO(BaseModel):
    id: int
    yyyymmdd: str
    title: str
    content: str
