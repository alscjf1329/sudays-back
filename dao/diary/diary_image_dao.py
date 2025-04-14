from sqlalchemy.orm import Session, joinedload
from model.diary.diary_image import DiaryImage
import uuid
from typing import Optional

class DiaryImageDAO:
    def __init__(self, db: Session):
        self.db = db
        
    def save(self, diary_image: DiaryImage) -> DiaryImage:
        try:
            self.db.add(diary_image)
            self.db.commit()
            self.db.refresh(diary_image)
            return diary_image
        except Exception as e:
            self.db.rollback()
            raise e

    def save_all(self, diary_images: list[DiaryImage]) -> list[DiaryImage]:
        try:
            self.db.add_all(diary_images)
            self.db.commit()
            for diary_image in diary_images:
                self.db.refresh(diary_image)
            return diary_images
        except Exception as e:
            self.db.rollback()
            raise e

    def find_by_id(self, diary_image_id: uuid.UUID) -> Optional[DiaryImage]:
        return self.db.query(DiaryImage).filter(DiaryImage.id == diary_image_id).first()

    def find_by_id_with_diary(self, diary_image_id: uuid.UUID) -> Optional[DiaryImage]:
        return self.db.query(DiaryImage).\
            options(joinedload(DiaryImage.diary)).\
            filter(DiaryImage.id == diary_image_id).\
            first()

    def find_by_ids(self, diary_image_ids: list[uuid.UUID]) -> list[DiaryImage]:
        return self.db.query(DiaryImage).filter(DiaryImage.id.in_(diary_image_ids)).all()

    def find_by_diary_id(self, diary_id: uuid.UUID) -> list[DiaryImage]:
        return self.db.query(DiaryImage).filter(DiaryImage.diary_id == diary_id).all()
        
    def delete(self, diary_image_id: uuid.UUID) -> None:
        diary_image = self.find_by_id(diary_image_id)
        if diary_image:
            self.db.delete(diary_image)
            self.db.commit()
