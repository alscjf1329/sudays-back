from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from dto.diary_dto import SaveDiaryRequestDTO, SaveDiaryResponseDTO, GetDiaryResponseDTO
from config.database import get_db
from dao.diary import DiaryDAO
from model.diary import Diary
import os
import uuid
from config.logger import get_logger
from datetime import datetime
from typing import Optional
router = APIRouter(prefix="/diary")

logger = get_logger()

def validate_date_format(yyyymmdd: str) -> bool:
    try:
        datetime.strptime(yyyymmdd, "%Y%m%d")
        return True
    except ValueError:
        return False

@router.get("/{yyyymmdd}", response_model=Optional[GetDiaryResponseDTO])
async def get_diary(yyyymmdd: str, db: Session = Depends(get_db)):
    if not validate_date_format(yyyymmdd):
        raise HTTPException(status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYYMMDD)")
    
    diary_dao = DiaryDAO(db)
    diary = diary_dao.find_by_yyyymmdd(yyyymmdd)
    if diary is None:
        return None
    return GetDiaryResponseDTO(
        id=diary.id,
        content=diary.content,
        image_urls=diary.image_urls
    )

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    UPLOAD_DIR = os.getenv("IMAGE_DIR")
    if not UPLOAD_DIR:
        raise ValueError("IMAGE_DIR 환경 변수가 설정되지 않았습니다.")
    
    try:
        logger.info(f"이미지 업로드 시작: {file.filename}")
        
        # 파일 확장자 확인
        file_extension = os.path.splitext(file.filename)[1]
        if file_extension.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
            logger.warning(f"지원하지 않는 이미지 형식: {file_extension}")
            raise ValueError("지원하지 않는 이미지 형식입니다.")
        
        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        logger.debug(f"생성된 파일 경로: {file_path}")
        
        # 파일 저장
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        logger.info(f"이미지 저장 완료: {unique_filename}")
        
        # 이미지 URL 반환
        return {"image_url": f"{UPLOAD_DIR}/{unique_filename}"}
        
    except Exception as e:
        logger.error(f"이미지 업로드 중 오류가 발생했습니다: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=SaveDiaryResponseDTO)
async def save_diary(diary: SaveDiaryRequestDTO, db: Session = Depends(get_db)):
    try:
        logger.info("일기 저장 시작")
        logger.debug(f"저장할 일기 내용: {diary.content[:20]}...")
        
        if not validate_date_format(diary.yyyymmdd):
            raise HTTPException(status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYYMMDD)")
        
        # Diary 모델 인스턴스 생성
        new_diary = Diary(
            yyyymmdd=diary.yyyymmdd,
            content=diary.content,
            image_urls=diary.image_urls if hasattr(diary, 'image_urls') else []
        )
        
        # DiaryDAO를 통해 DB에 저장
        diary_dao = DiaryDAO(db)
        saved_diary = diary_dao.save(new_diary)
        logger.info(f"일기 저장 완료 (ID: {saved_diary.id})")
        
        # DTO로 변환하여 반환
        return SaveDiaryResponseDTO(
            id=saved_diary.id,
            yyyymmdd=saved_diary.yyyymmdd,
            content=saved_diary.content,
            image_urls=saved_diary.image_urls
        )
        
    except Exception as e:
        logger.error(f"일기 저장 중 오류가 발생했습니다: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))