from sqlalchemy.orm import Session
from dao.diary.diary_dao import DiaryDAO
from dao.diary.diary_image_dao import DiaryImageDAO
from model.diary.diary import Diary
from model.diary.diary_image import DiaryImage
from datetime import datetime, timezone
import os
import uuid
from typing import Optional, List
from config.logger import get_logger
from fastapi import UploadFile, HTTPException
from fastapi import status

logger = get_logger(__name__)

class DiaryService:
    def __init__(self, db: Session):
        self.db = db
        self.diary_dao = DiaryDAO(db)
        self.diary_image_dao = DiaryImageDAO(db)
        self.ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
        self.MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

    def validate_date_format(self, yyyymmdd: str) -> bool:
        try:
            datetime.strptime(yyyymmdd, "%Y%m%d")
            return True
        except ValueError:
            return False

    def get_diary(self, yyyymmdd: str, member_id: uuid.UUID) -> Optional[Diary]:
        if not self.validate_date_format(yyyymmdd):
            raise ValueError("올바른 날짜 형식이 아닙니다. (YYYYMMDD)")

        return self.diary_dao.find_by_yyyymmdd(member_id, yyyymmdd)

    async def upsert_diary(self, yyyymmdd: str, content: str, images: List[UploadFile] = None, member_id: uuid.UUID = None) -> Diary:
        try:
            logger.info(f"일기 저장 시작 - 날짜: {yyyymmdd}, 사용자: {member_id}")

            if not self.validate_date_format(yyyymmdd):
                raise ValueError("올바른 날짜 형식이 아닙니다. (YYYYMMDD)")

            if member_id is None:
                raise ValueError("사용자 ID가 필요합니다.")

            if not content.strip():
                raise ValueError("일기 내용은 비어있을 수 없습니다.")

            # 이미지 업로드 및 메타데이터 저장 처리
            image_ids = []
            diary_images = []

            if images:
                if len(images) > 5:
                    raise ValueError("최대 5개의 이미지만 업로드할 수 있습니다.")

                for image in images:
                    file_extension = os.path.splitext(image.filename)[1].lower()
                    
                    if file_extension not in self.ALLOWED_EXTENSIONS:
                        logger.error(f"지원하지 않는 이미지 형식: {image.filename} (확장자: {file_extension})")
                        raise ValueError(f"지원하지 않는 이미지 형식입니다. 허용된 형식: {', '.join(self.ALLOWED_EXTENSIONS)}")

                    try:
                        # 이미지 크기 확인
                        image_content = await image.read()
                        if len(image_content) > self.MAX_IMAGE_SIZE:
                            raise ValueError(f"이미지 크기가 너무 큽니다. 최대 {self.MAX_IMAGE_SIZE/1024/1024}MB까지 허용됩니다.")
                        
                        image_id = uuid.uuid4()
                        file_name = str(image_id)
                        file_path = os.path.join(os.getenv("IMAGE_DIR"), f"{file_name}{file_extension}")

                        # 파일 저장
                        with open(file_path, "wb") as buffer:
                            buffer.write(image_content)

                        # 이미지 메타데이터 저장
                        diary_image = DiaryImage(
                            id=image_id,
                            diary_id=None,  # 일기 ID는 나중에 설정
                            file_name=file_name,
                            extension=file_extension,
                            base_path=os.getenv("IMAGE_DIR"),
                        )
                        diary_images.append(diary_image)
                        image_ids.append(image_id)
                        logger.info(f"이미지 저장 완료: {file_name}")
                    except Exception as e:
                        logger.error(f"이미지 처리 중 오류 발생: {str(e)}")
                        raise ValueError(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")

            # 기존 일기 확인
            existing_diary = self.diary_dao.find_by_yyyymmdd(member_id, yyyymmdd)
            
            if existing_diary:
                # 기존 일기 업데이트
                existing_diary.content = content
                existing_diary.image_ids = image_ids
                existing_diary.updated_at = datetime.now(timezone.utc)
                saved_diary = self.diary_dao.save(existing_diary)
                logger.info(f"일기 업데이트 완료 (ID: {saved_diary.id})")
            else:
                # 새로운 일기 저장
                diary = Diary(
                    member_id=member_id, 
                    yyyymmdd=yyyymmdd, 
                    content=content,
                    image_ids=image_ids
                )
                saved_diary = self.diary_dao.save(diary)
                logger.info(f"일기 저장 완료 (ID: {saved_diary.id})")

            # 이미지 메타데이터에 일기 ID 설정 및 저장
            for diary_image in diary_images:
                diary_image.diary_id = saved_diary.id
                self.diary_image_dao.save(diary_image)

            return saved_diary

        except ValueError as e:
            logger.error(f"일기 저장 중 유효성 검사 오류: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"일기 저장 중 예상치 못한 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="일기 저장 중 오류가 발생했습니다."
            )

    def get_diary_image(self, diary_image_id: str, member_id: uuid.UUID) -> tuple[bytes, str]:
        try:
            image_uuid = uuid.UUID(diary_image_id)
            
            diary_image = self.diary_image_dao.find_by_id(image_uuid)
            if diary_image is None:
                raise ValueError("이미지를 찾을 수 없습니다.")

            diary = self.diary_dao.find_by_id(diary_image.diary_id)
            if diary is None or diary.member_id != member_id:
                raise ValueError("이미지에 접근할 권한이 없습니다.")

            file_path = os.path.join(diary_image.base_path, f"{diary_image.file_name}{diary_image.extension}")
            
            try:
                with open(file_path, "rb") as f:
                    image_data = f.read()
            except FileNotFoundError:
                raise ValueError("이미지 파일을 찾을 수 없습니다.")
            except Exception as e:
                raise ValueError(f"이미지 파일 읽기 중 오류가 발생했습니다: {str(e)}")

            return image_data, diary_image.extension.lstrip('.')
            
        except ValueError as e:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="이미지 조회 중 오류가 발생했습니다."
            )
