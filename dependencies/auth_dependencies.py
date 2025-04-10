from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dao.member.member_dao import MemberDAO
from dto.auth_dto import Member
from config.jwt_config import verify_token
from config.database import get_db

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
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    member_dao = MemberDAO(db)
    member = member_dao.get_member_by_email(email)
    if member is None:
        raise credentials_exception
        
    return Member(**member) 