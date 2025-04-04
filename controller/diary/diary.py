from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from dto.diary_dto import SaveDiaryResponseDTO, GetDiaryResponseDTO
from config.database import get_db
from dao.diary import DiaryDAO
from model.diary import Diary
import os
import uuid
from config.logger import get_logger
from datetime import datetime
from typing import Optional
from fastapi.responses import Response
from dao.diary_image_dao import DiaryImageDAO
from model.diary_image import DiaryImage

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
        raise HTTPException(
            status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYYMMDD)"
        )

    diary_dao = DiaryDAO(db)

    diary = diary_dao.find_by_yyyymmdd(yyyymmdd)
    if diary is None:
        return None

    return GetDiaryResponseDTO(
        id=diary.id, yyyymmdd=diary.yyyymmdd, content=diary.content, image_ids=diary.image_ids
    )


@router.post("/", response_model=SaveDiaryResponseDTO)
async def upsert_diary(
    yyyymmdd: str = Form(...),
    content: str = Form(...),
    images: list[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    try:
        logger.info("일기 저장 시작")
        logger.debug(f"저장할 일기 내용: {content[:20]}...")

        if not validate_date_format(yyyymmdd):
            raise HTTPException(
                status_code=400, detail="올바른 날짜 형식이 아닙니다. (YYYYMMDD)"
            )

        # 이미지 업로드 및 메타데이터 저장 처리
        image_ids = []
        diary_images = []
        diary_image_dao = DiaryImageDAO(db)

        if images:
            for image in images:
                file_extension = os.path.splitext(image.filename)[1].lower()
                
                if file_extension not in [".jpg", ".jpeg", ".png", ".gif"]:
                    logger.warning(f"지원하지 않는 이미지 형식: {file_extension}")
                    continue

                try:
                    image_id = uuid.uuid4()
                    file_name = image_id
                    file_path = os.path.join(os.getenv("IMAGE_DIR"), f"{file_name}{file_extension}")

                    # 파일 저장
                    image_content = await image.read()
                    with open(file_path, "wb") as buffer:
                        buffer.write(image_content)

                    # 이미지 메타데이터 저장
                    diary_image = DiaryImage(
                        id=image_id,
                        file_name=file_name,
                        extension=file_extension,
                        base_path=os.getenv("IMAGE_DIR"),
                    )
                    diary_images.append(diary_image)
                    image_ids.append(image_id)
                    logger.info(f"이미지 저장 완료: {file_name}")
                    diary_image_dao.save(diary_image)
                except Exception as e:
                    logger.error(f"이미지 처리 중 오류 발생: {str(e)}")
                    continue
        
        # 일기 저장
        diary = Diary(yyyymmdd=yyyymmdd, content=content, image_ids=image_ids)
        image_ids = diary_image_dao.save_all(diary_images)
        saved_diary = DiaryDAO(db).save(diary)
        logger.info(f"일기 저장 완료 (ID: {saved_diary.id})")

        return SaveDiaryResponseDTO(
            id=saved_diary.id,
            yyyymmdd=saved_diary.yyyymmdd,
            content=saved_diary.content,
            image_ids=saved_diary.image_ids,
        )

    except Exception as e:
        logger.error(f"일기 저장 중 오류가 발생했습니다: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/{diary_image_id}", response_model=None)
async def get_diary_image(diary_image_id: str, db: Session = Depends(get_db)):
    image_uuid = uuid.UUID(diary_image_id)
    logger.info(f"이미지 UUID: {image_uuid}")
    diary_image_dao = DiaryImageDAO(db)
    diary_image = diary_image_dao.find_by_id(image_uuid)
    logger.debug(f"이미지 정보: {diary_image}")
    if diary_image is None:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    file_path = os.path.join(diary_image.base_path, f"{diary_image.file_name}{diary_image.extension}")
    logger.debug(f"이미지 파일 경로: {file_path}")
    try:
        with open(file_path, "rb") as f:
            image_data = f.read()
    except:
        raise HTTPException(status_code=404, detail="이미지 파일을 찾을 수 없습니다.")

    return Response(content=image_data, media_type=f"image/{diary_image.extension.lstrip('.')}")
