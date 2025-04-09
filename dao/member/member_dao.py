from sqlalchemy.orm import Session
from model.member.member import Member, MemberRole, MemberGrade
from typing import Optional, List
from util.hash_util import PasswordUtil

class MemberDAO:
    def __init__(self, session: Session):
        self.session = session

    def create_member(self, email: str, password: str, nickname: str) -> Member:
        hashed_password = PasswordUtil.hash_password(password)
        member = Member(email=email, password=hashed_password, nickname=nickname)
        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)
        return member

    def get_member_by_id(self, member_id: int) -> Optional[Member]:
        return self.session.query(Member).filter(Member.id == member_id).first()

    def get_member_by_email(self, email: str) -> Optional[Member]:
        return self.session.query(Member).filter(Member.email == email).first()

    def get_members_by_role(self, role: MemberRole) -> List[Member]:
        return self.session.query(Member).filter(Member.role == role).all()

    def get_members_by_grade(self, grade: MemberGrade) -> List[Member]:
        return self.session.query(Member).filter(Member.grade == grade).all()

    def verify_member_password(self, email: str, password: str) -> bool:
        member = self.get_member_by_email(email)
        if not member:
            return False
        return PasswordUtil.verify_password(password, member.password)

    def update_member(self, member_id: int, **kwargs) -> Optional[Member]:
        member = self.get_member_by_id(member_id)
        if member:
            for key, value in kwargs.items():
                if hasattr(member, key):
                    if key == 'password':
                        value = PasswordUtil.hash_password(value)
                    setattr(member, key, value)
            self.session.commit()
            self.session.refresh(member)
        return member

    def delete_member(self, member_id: int) -> bool:
        member = self.get_member_by_id(member_id)
        if member:
            self.session.delete(member)
            self.session.commit()
            return True
        return False 