from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from config.database import get_db
from config.logger import get_logger
from service.email.email_service import EmailService
from dto.email_verification_dto import (
    SendVerificationCodeRequestDTO,
    SendVerificationCodeResponseDTO,
    VerifyCodeRequestDTO,
    VerifyCodeResponseDTO
)
import re
from datetime import datetime, timedelta

router = APIRouter()
logger = get_logger(__name__)

# 로거 초기화 확인
logger.info("verify_controller 로거 초기화 완료")

def validate_email_format(email: str) -> bool:
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(pattern, email) is not None
    logger.debug(f"이메일 형식 검증: {email} -> {is_valid}")
    return is_valid

def validate_verification_code(code: str) -> bool:
    """인증코드 형식 검증 (6자리 숫자)"""
    is_valid = len(code) == 6 and code.isdigit()
    logger.debug(f"인증코드 형식 검증: {code} -> {is_valid}")
    return is_valid

@router.post("/email/send-verification", response_model=SendVerificationCodeResponseDTO)
async def send_verification_code(
    request: SendVerificationCodeRequestDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    이메일 인증코드 발송 API
    """
    logger.info(f"=== 인증코드 발송 요청 시작 ===")
    logger.info(f"요청 이메일: {request.email}")
    logger.info(f"요청 데이터: {request}")
    
    # 이메일 형식 검증
    if not validate_email_format(request.email):
        logger.warning(f"이메일 형식 검증 실패: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 이메일 형식이 아닙니다"
        )
    
    logger.info(f"이메일 형식 검증 통과: {request.email}")
    
    try:
        logger.info("EmailService 인스턴스 생성 시작")
        email_service = EmailService(db)
        logger.info("EmailService 인스턴스 생성 완료")
        
        # 인증 레코드 생성
        logger.info("인증 레코드 생성 시작")
        verification = email_service.create_verification_record(request.email)
        logger.info(f"인증 레코드 생성 완료 - ID: {verification.id}, 코드: {verification.verification_code}")
        
        # 백그라운드에서 이메일 발송 (응답 속도 향상)
        logger.info("백그라운드 이메일 발송 작업 추가")
        background_tasks.add_task(
            email_service.send_verification_email,
            request.email, 
            verification.verification_code
        )
        
        logger.info(f"인증코드 발송 성공 - 이메일: {request.email}")
        return SendVerificationCodeResponseDTO(
            message="인증코드가 이메일로 발송되었습니다",
            email=request.email
        )
        
    except ValueError as e:
        logger.warning(f"인증코드 발송 중 검증 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        logger.error("HTTPException 발생 - 상위로 전파")
        raise
    except Exception as e:
        logger.error(f"인증코드 발송 중 예상치 못한 오류 발생: {str(e)}")
        logger.error(f"오류 타입: {type(e).__name__}")
        import traceback
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류가 발생했습니다"
        )

@router.post("/email/verify-code", response_model=VerifyCodeResponseDTO)
async def verify_code(
    request: VerifyCodeRequestDTO,
    db: Session = Depends(get_db)
):
    """
    이메일 인증코드 검증 API
    """
    logger.info(f"=== 인증코드 검증 요청 시작 ===")
    logger.info(f"요청 이메일: {request.email}")
    logger.info(f"요청 인증코드: {request.verification_code}")
    
    # 입력값 검증
    if not validate_email_format(request.email):
        logger.warning(f"이메일 형식 검증 실패: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 이메일 형식이 아닙니다"
        )
    
    if not validate_verification_code(request.verification_code):
        logger.warning(f"인증코드 형식 검증 실패: {request.verification_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증코드는 6자리 숫자여야 합니다"
        )
    
    logger.info(f"입력값 검증 통과 - 이메일: {request.email}, 코드: {request.verification_code}")
    
    try:
        logger.info("EmailService 인스턴스 생성 시작")
        email_service = EmailService(db)
        logger.info("EmailService 인스턴스 생성 완료")
        
        # 인증코드 검증
        logger.info("인증코드 검증 시작")
        is_verified = email_service.verify_code(request.email, request.verification_code)
        logger.info(f"인증코드 검증 결과: {is_verified}")
        
        if not is_verified:
            logger.warning(f"인증코드 검증 실패 - 이메일: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인증코드가 올바르지 않거나 만료되었습니다"
            )
        
        logger.info(f"인증코드 검증 성공 - 이메일: {request.email}")
        return VerifyCodeResponseDTO(
            message="이메일 인증이 완료되었습니다",
            is_verified=True,
            email=request.email
        )
        
    except HTTPException:
        logger.error("HTTPException 발생 - 상위로 전파")
        raise
    except Exception as e:
        logger.error(f"인증코드 검증 중 예상치 못한 오류 발생: {str(e)}")
        logger.error(f"오류 타입: {type(e).__name__}")
        import traceback
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류가 발생했습니다"
        )

@router.get("/email/verification-status/{email}")
async def check_verification_status(
    email: str,
    db: Session = Depends(get_db)
):
    """
    이메일 인증 상태 확인 API
    """
    logger.info(f"=== 인증 상태 확인 요청 시작 ===")
    logger.info(f"요청 이메일: {email}")
    
    # 이메일 형식 검증
    if not validate_email_format(email):
        logger.warning(f"이메일 형식 검증 실패: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 이메일 형식이 아닙니다"
        )
    
    logger.info(f"이메일 형식 검증 통과: {email}")
    
    try:
        logger.info("EmailService 인스턴스 생성 시작")
        email_service = EmailService(db)
        logger.info("EmailService 인스턴스 생성 완료")
        
        logger.info("인증 상태 확인 시작")
        is_verified = email_service.is_email_verified(email)
        logger.info(f"인증 상태 확인 결과: {is_verified}")
        
        result = {
            "email": email,
            "is_verified": is_verified,
            "checked_at": datetime.utcnow().isoformat()
        }
        logger.info(f"응답 데이터: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"인증 상태 확인 중 예상치 못한 오류 발생: {str(e)}")
        logger.error(f"오류 타입: {type(e).__name__}")
        import traceback
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류가 발생했습니다"
        ) 