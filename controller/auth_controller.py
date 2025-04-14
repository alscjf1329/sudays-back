from fastapi import APIRouter, HTTPException, status, Response, Depends, Form, Cookie
from datetime import timedelta
from sqlalchemy.orm import Session

from config.jwt_config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from dto.auth_dto import MemberCreate, Member
from service.member.member_service import MemberService
from dependencies.auth_dependencies import get_current_member, oauth2_scheme
from config.database import get_db
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(member: MemberCreate, db: Session = Depends(get_db)):
    """
    회원가입 API
    """
    logger.info(f"회원가입 시도 - 이메일: {member.email}, 닉네임: {member.nickname}")
    member_service = MemberService(db)
    
    if member_service.get_member_by_email(member.email):
        logger.warning(f"중복된 이메일로 회원가입 시도: {member.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    created_member = member_service.register_member(
        email=member.email,
        password=member.password,
        nickname=member.nickname
    )
    
    if not created_member:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 중 오류가 발생했습니다"
        )
    
    logger.info(f"회원가입 완료 - 이메일: {member.email}")
    return {"message": "회원가입이 완료되었습니다"}

@router.post("/login", response_model=None)
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    로그인 API
    """
    logger.info(f"로그인 시도 - 이메일: {email}")
    member_service = MemberService(db)
    
    member = member_service.login(email, password)
    if not member:
        logger.warning(f"로그인 실패 - 이메일: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": member.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": member.email})
    
    logger.info(f"로그인 성공 - 이메일: {email}")
    response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    return {"message": "로그인 성공"}

@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None)
):
    """
    액세스 토큰 갱신 API
    """
    logger.info("토큰 갱신 요청")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 존재하지 않습니다"
        )
    
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": payload["sub"]}, expires_delta=access_token_expires
    )
    
    response.headers["Authorization"] = f"Bearer {access_token}"
    return {"message": "토큰이 갱신되었습니다"}

@router.post("/logout")
async def logout(response: Response):
    """
    로그아웃 API
    """
    logger.info("로그아웃 요청 처리")
    response.delete_cookie("refresh_token")
    return {"message": "로그아웃되었습니다"}

@router.get("/me", response_model=Member)
async def read_members_me(current_member: Member = Depends(get_current_member)):
    """
    현재 로그인한 사용자 정보 조회 API
    """
    logger.debug(f"사용자 정보 조회 - 이메일: {current_member.email}")
    return current_member

@router.get("/protected")
async def protected_route(current_member: Member = Depends(get_current_member)):
    """
    보호된 리소스 접근 API
    """
    logger.debug(f"보호된 리소스 접근 - 사용자: {current_member.email}")
    return {"message": f"안녕하세요, {current_member.nickname}님! 보호된 리소스에 접근하셨습니다."}