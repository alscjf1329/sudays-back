from sqlalchemy.orm import Session
from model.member.member import Member, MemberRole, MemberGrade
from typing import Optional, List
import uuid
from config.logger import get_logger

logger = get_logger()

class MemberDAO:
    def __init__(self, session: Session):
        self.session = session

    def create_member(self, email: str, password: str, nickname: str) -> Optional[Member]:
        try:
            member = Member(email=email, password=password, nickname=nickname)
            self.session.add(member)
            self.session.commit()
            self.session.refresh(member)
            return member
        except Exception as e:
            logger.error(f"회원 생성 중 오류 발생: {str(e)}")
            self.session.rollback()
            return None

    def get_member_by_id(self, member_id: uuid.UUID) -> Optional[Member]:
        return self.session.query(Member).filter(Member.id == member_id).first()

    def get_member_by_email(self, email: str) -> Optional[Member]:
        return self.session.query(Member).filter(Member.email == email).first()

    def get_members_by_role(self, role: MemberRole) -> List[Member]:
        return self.session.query(Member).filter(Member.role == role).all()

    def get_members_by_grade(self, grade: MemberGrade) -> List[Member]:
        return self.session.query(Member).filter(Member.grade == grade).all()

    def update_member(self, member_id: uuid.UUID, **kwargs) -> Optional[Member]:
        try:
            member = self.get_member_by_id(member_id)
            if not member:
                return None

            allowed_fields = {'nickname', 'password', 'role', 'grade'}  # 허용된 필드 목록
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(member, key):
                    setattr(member, key, value)

            self.session.commit()
            self.session.refresh(member)
            return member
        except Exception as e:
            logger.error(f"회원 정보 업데이트 중 오류 발생: {str(e)}")
            self.session.rollback()
            return None

    def delete_member(self, member_id: uuid.UUID) -> bool:
        try:
            member = self.get_member_by_id(member_id)
            if member:
                self.session.delete(member)
                self.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"회원 삭제 중 오류 발생: {str(e)}")
            self.session.rollback()
            return False 