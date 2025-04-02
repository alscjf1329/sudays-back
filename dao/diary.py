from sqlalchemy.orm import Session
from model.diary import Diary, DiarySaveDTO
import uuid
from typing import Optional

class DiaryDAO:
    def __init__(self, db: Session):
        self.db = db
        
    def save(self, diary: DiarySaveDTO) -> Diary:
        try:
            self.db.add(diary)
            self.db.commit()
            self.db.refresh(diary)
            return diary
        except Exception as e:
            self.db.rollback()
            raise e
            
    def find_by_id(self, diary_id: uuid.UUID) -> Optional[Diary]:
        return self.db.query(Diary).filter(Diary.id == diary_id).first()
        
    def find_by_yyyymmdd(self, yyyymmdd: str) -> Optional[Diary]:
        return self.db.query(Diary).filter(Diary.yyyymmdd == yyyymmdd).first()
        
    def delete(self, diary_id: uuid.UUID) -> None:
        diary = self.find_by_id(diary_id)
        if diary:
            self.db.delete(diary)
            self.db.commit()
