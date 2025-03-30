from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dto.diary_dto import DiarySaveRequestDTO, DiarySaveResponseDTO
from config.database import get_db
from dao.diary import DiaryDAO
from model.diary import Diary

router = APIRouter(prefix="/diary")

@router.post("/")
async def save_diary(diary: DiarySaveRequestDTO, db: Session = Depends(get_db)):
    try:
        # Diary 모델 인스턴스 생성
        new_diary = Diary(
            yyyymmdd=diary.yyyymmdd,
            title=diary.title,
            content=diary.content
        )
        
        # DiaryDAO를 통해 DB에 저장
        diary_dao = DiaryDAO(db)
        saved_diary = diary_dao.save(new_diary)
        
        # DTO로 변환하여 반환
        return DiarySaveResponseDTO(
            id=saved_diary.id,
            yyyymmdd=saved_diary.yyyymmdd,
            title=saved_diary.title,
            content=saved_diary.content
        )
        
    except Exception as e:
        raise e