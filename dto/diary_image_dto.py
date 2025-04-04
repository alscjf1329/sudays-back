from pydantic import BaseModel
from typing import List
import uuid

class GetDiaryImageRequestDTO(BaseModel):
    ids: List[uuid.UUID]
