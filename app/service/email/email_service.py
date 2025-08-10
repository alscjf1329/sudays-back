import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Optional

from model.member.email_verification import EmailVerification
from config.logger import get_logger
from config.email_config import EmailConfig

logger = get_logger(__name__)

class EmailService:
    def __init__(self, db: Session):
        self.db = db
        
        # 설정 검증
        EmailConfig.validate_config()
        
        self.fastmail = FastMail(
            ConnectionConfig(
                MAIL_USERNAME=EmailConfig.MAIL_USERNAME,
                MAIL_PASSWORD=EmailConfig.MAIL_PASSWORD,
                MAIL_FROM=EmailConfig.MAIL_FROM,
                MAIL_PORT=EmailConfig.MAIL_PORT,
                MAIL_SERVER=EmailConfig.MAIL_SERVER,
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True
            )
        )

    def generate_verification_code(self) -> str:
        """인증코드 생성"""
        return ''.join(random.choices(string.digits, k=EmailConfig.VERIFICATION_CODE_LENGTH))

    def create_verification_record(self, email: str) -> EmailVerification:
        """이메일 인증 레코드 생성"""
        
        # Rate Limiting 체크
        if EmailConfig.ENABLE_RATE_LIMITING:
            recent_attempts = self.db.query(EmailVerification).filter(
                EmailVerification.email == email,
                EmailVerification.created_at >= datetime.utcnow() - timedelta(minutes=EmailConfig.RATE_LIMIT_MINUTES)
            ).count()
            
            if recent_attempts >= EmailConfig.MAX_VERIFICATION_ATTEMPTS:
                raise ValueError(EmailConfig.get_rate_limit_message())
        
        # 기존 미인증 레코드 삭제
        self.db.query(EmailVerification).filter(
            EmailVerification.email == email,
            EmailVerification.is_verified == False
        ).delete()
        
        verification_code = self.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=EmailConfig.VERIFICATION_CODE_EXPIRE_MINUTES)
        
        verification = EmailVerification(
            email=email,
            verification_code=verification_code,
            expires_at=expires_at
        )
        
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        
        if EmailConfig.LOG_VERIFICATION_ATTEMPTS:
            logger.info(f"인증코드 생성 - 이메일: {email}, 코드: {verification_code}")
        
        return verification

    async def send_verification_email(self, email: str, verification_code: str) -> bool:
        """인증코드 이메일 발송"""
        try:
            html_content = f"""
            <html>
            <body>
                <h2>{EmailConfig.EMAIL_TEMPLATE_TITLE}</h2>
                <p>{EmailConfig.EMAIL_TEMPLATE_GREETING}</p>
                <p>{EmailConfig.EMAIL_TEMPLATE_INSTRUCTION}</p>
                <h1 style="color: #007bff; font-size: 32px; text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                    {verification_code}
                </h1>
                <p><strong>{EmailConfig.get_expiry_message()}</strong></p>
                <p>{EmailConfig.EMAIL_TEMPLATE_SECURITY_NOTICE}</p>
                <hr>
                <p style="color: #6c757d; font-size: 12px;">
                    {EmailConfig.EMAIL_TEMPLATE_FOOTER}
                </p>
            </body>
            </html>
            """
            
            message = MessageSchema(
                subject=EmailConfig.EMAIL_SUBJECT,
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            
            if EmailConfig.LOG_EMAIL_SEND_RESULTS:
                logger.info(f"인증코드 이메일 발송 성공: {email}")
            return True
            
        except Exception as e:
            if EmailConfig.LOG_EMAIL_SEND_RESULTS:
                logger.error(f"인증코드 이메일 발송 실패: {email}, 오류: {str(e)}")
            return False

    def get_verification_by_email(self, email: str) -> Optional[EmailVerification]:
        """이메일로 인증 레코드 조회"""
        return self.db.query(EmailVerification).filter(
            EmailVerification.email == email
        ).first()

    def verify_code(self, email: str, verification_code: str) -> bool:
        """인증코드 검증"""
        verification = self.get_verification_by_email(email)
        
        if not verification:
            logger.warning(f"인증 레코드 없음: {email}")
            return False
        
        if not verification.is_valid:
            logger.warning(f"인증코드 유효하지 않음: {email}")
            return False
        
        if verification.verification_code != verification_code:
            logger.warning(f"인증코드 불일치: {email}")
            return False
        
        # 인증 성공
        verification.is_verified = True
        verification.verified_at = datetime.utcnow()
        self.db.commit()
        
        # 인증 완료 후 해당 이메일의 모든 미인증 레코드 삭제
        if EmailConfig.ENABLE_AUTO_CLEANUP:
            self.db.query(EmailVerification).filter(
                EmailVerification.email == email,
                EmailVerification.is_verified == False
            ).delete()
            self.db.commit()
        
        logger.info(f"이메일 인증 성공: {email}")
        return True

    def is_email_verified(self, email: str) -> bool:
        """이메일이 인증되었는지 확인"""
        verification = self.get_verification_by_email(email)
        return verification and verification.is_verified 