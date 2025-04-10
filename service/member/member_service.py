from typing import Optional, List
from dao.member.member_dao import MemberDAO
from model.member.member import Member, MemberRole, MemberGrade
from sqlalchemy.orm import Session
from util.hash_util import HashUtil
import logging

logger = logging.getLogger(__name__)

class MemberService:
    def __init__(self, session: Session):
        self.member_dao = MemberDAO(session)
        self.hash_util = HashUtil()

    def register_member(self, email: str, password: str, nickname: str) -> Optional[Member]:
        """
        새로운 회원을 등록합니다.
        """
        try:
            # 이메일 중복 체크
            existing_member = self.member_dao.get_member_by_email(email)
            if existing_member:
                logger.warning(f"이미 존재하는 이메일로 회원가입 시도: {email}")
                return None

            # 비밀번호 해싱
            hashed_password = self.hash_util.hash_password(password)
            
            # 회원 생성
            return self.member_dao.create_member(email, hashed_password, nickname)
        except Exception as e:
            logger.error(f"회원가입 중 오류 발생: {str(e)}")
            return None

    def login(self, email: str, password: str) -> Optional[Member]:
        """
        회원 로그인을 처리합니다.
        """
        try:
            member = self.member_dao.get_member_by_email(email)
            if not member:
                logger.warning(f"존재하지 않는 이메일로 로그인 시도: {email}")
                return None

            if self.hash_util.verify_password(password, member.password):
                return member
            return None
        except Exception as e:
            logger.error(f"로그인 중 오류 발생: {str(e)}")
            return None

    def get_member(self, member_id: int) -> Optional[Member]:
        """
        회원 ID로 회원 정보를 조회합니다.
        """
        return self.member_dao.get_member_by_id(member_id)

    def get_member_by_email(self, email: str) -> Optional[Member]:
        """
        이메일로 회원 정보를 조회합니다.
        """
        return self.member_dao.get_member_by_email(email)

    def get_members_by_role(self, role: MemberRole) -> List[Member]:
        """
        역할별로 회원 목록을 조회합니다.
        """
        return self.member_dao.get_members_by_role(role)

    def get_members_by_grade(self, grade: MemberGrade) -> List[Member]:
        """
        등급별로 회원 목록을 조회합니다.
        """
        return self.member_dao.get_members_by_grade(grade)

    def update_member(self, member_id: int, **kwargs) -> Optional[Member]:
        """
        회원 정보를 업데이트합니다.
        """
        try:
            # 회원 존재 여부 확인
            member = self.member_dao.get_member_by_id(member_id)
            if not member:
                logger.warning(f"존재하지 않는 회원 정보 업데이트 시도: {member_id}")
                return None

            # 비밀번호가 포함된 경우 해싱
            if 'password' in kwargs:
                kwargs['password'] = self.hash_util.hash_password(kwargs['password'])

            return self.member_dao.update_member(member_id, **kwargs)
        except Exception as e:
            logger.error(f"회원 정보 업데이트 중 오류 발생: {str(e)}")
            return None

    def delete_member(self, member_id: int) -> bool:
        """
        회원을 삭제합니다.
        """
        try:
            # 회원 존재 여부 확인
            member = self.member_dao.get_member_by_id(member_id)
            if not member:
                logger.warning(f"존재하지 않는 회원 삭제 시도: {member_id}")
                return False

            return self.member_dao.delete_member(member_id)
        except Exception as e:
            logger.error(f"회원 삭제 중 오류 발생: {str(e)}")
            return False 