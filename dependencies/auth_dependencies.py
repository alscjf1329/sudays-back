from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dao.member.member_dao import MemberDAO
from dto.auth_dto import Member
from config.jwt_config import verify_token
from config.database import get_db
from config.logger import get_logger

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_member(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Member:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"토큰 검증 시작: {token[:10]}...")
    payload = verify_token(token)
    if payload is None:
        logger.warning("토큰 검증 실패: 유효하지 않은 토큰")
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        logger.warning("토큰 검증 실패: 이메일 정보 없음")
        raise credentials_exception
        
    logger.info(f"사용자 조회 시작: {email}")
    member_dao = MemberDAO(db)
    member = member_dao.get_member_by_email(email)
    if member is None:
        logger.warning(f"사용자 조회 실패: {email} 존재하지 않음")
        raise credentials_exception
    
    logger.info(f"사용자 인증 성공: {email}")    
    return member