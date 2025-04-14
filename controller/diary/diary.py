from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, status
from sqlalchemy.orm import Session
from dto.diary_dto import SaveDiaryResponseDTO, GetDiaryResponseDTO
from config.database import get_db
from service.diary.diary_service import DiaryService
from fastapi.responses import Response, JSONResponse
from typing import Optional
from dependencies.auth_dependencies import get_current_member
from dto.auth_dto import MemberInfoDTO
from config.logger import get_logger

router = APIRouter(prefix="/diary")
logger = get_logger(__name__)


@router.get("/{yyyymmdd}", response_model=Optional[GetDiaryResponseDTO])
async def get_diary(
    yyyymmdd: str, 
    db: Session = Depends(get_db),
    current_member: MemberInfoDTO = Depends(get_current_member)
):
    """
    특정 날짜의 다이어리를 조회합니다.
    """
    logger.info(f"다이어리 조회 요청 - 날짜: {yyyymmdd}, 사용자: {current_member.email}")
    diary_service = DiaryService(db)
    
    try:
        diary = diary_service.get_diary(yyyymmdd, current_member.id)
        if diary is None:
            return None

        return GetDiaryResponseDTO(
            id=diary.id, 
            yyyymmdd=diary.yyyymmdd, 
            content=diary.content, 
            image_ids=diary.image_ids
        )
    except ValueError as e:
        logger.error(f"다이어리 조회 중 유효성 검사 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"다이어리 조회 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="다이어리 조회 중 오류가 발생했습니다."
        )


@router.post("/", response_model=SaveDiaryResponseDTO)
async def upsert_diary(
    yyyymmdd: str = Form(...),
    content: str = Form(...),
    images: list[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_member: MemberInfoDTO = Depends(get_current_member)
):
    """
    다이어리를 저장하거나 수정합니다.
    """
    logger.info(f"다이어리 저장/수정 요청 - 날짜: {yyyymmdd}, 사용자: {current_member.email}")
    diary_service = DiaryService(db)
    
    try:
        saved_diary = await diary_service.upsert_diary(yyyymmdd, content, images, current_member.id)
        return SaveDiaryResponseDTO(
            id=saved_diary.id,
            yyyymmdd=saved_diary.yyyymmdd,
            content=saved_diary.content,
            image_ids=saved_diary.image_ids,
        )
    except ValueError as e:
        logger.error(f"다이어리 저장 중 유효성 검사 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"다이어리 저장 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="다이어리 저장 중 오류가 발생했습니다."
        )


@router.get("/image/{diary_image_id}")
async def get_diary_image(
    diary_image_id: str, 
    db: Session = Depends(get_db),
    current_member: MemberInfoDTO = Depends(get_current_member)
):
    """
    다이어리 이미지를 조회합니다.
    """
    logger.info(f"다이어리 이미지 조회 요청 - 이미지ID: {diary_image_id}, 사용자: {current_member.email}")
    diary_service = DiaryService(db)
    
    try:
        image_data, extension = diary_service.get_diary_image(diary_image_id, current_member.id)
        return Response(
            content=image_data,
            media_type=f"image/{extension}",
            headers={"Cache-Control": "private, max-age=3600"}
        )
    except ValueError as e:
        logger.error(f"다이어리 이미지 조회 중 유효성 검사 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"다이어리 이미지 조회 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이미지 조회 중 오류가 발생했습니다."
        )
