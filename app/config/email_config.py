import os
from dotenv import load_dotenv

load_dotenv()

class EmailConfig:
    """이메일 인증 관련 설정"""
    
    # SMTP 설정
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    
    # 인증코드 설정
    VERIFICATION_CODE_LENGTH = int(os.getenv("VERIFICATION_CODE_LENGTH", 6))
    VERIFICATION_CODE_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_CODE_EXPIRE_MINUTES", 10))
    
    # Rate Limiting 설정
    MAX_VERIFICATION_ATTEMPTS = int(os.getenv("MAX_VERIFICATION_ATTEMPTS", 3))
    RATE_LIMIT_MINUTES = int(os.getenv("RATE_LIMIT_MINUTES", 20))
    
    # 이메일 템플릿 설정
    EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "[Sudays] 이메일 인증코드")
    EMAIL_TEMPLATE_TITLE = os.getenv("EMAIL_TEMPLATE_TITLE", "Sudays 이메일 인증")
    EMAIL_TEMPLATE_GREETING = os.getenv("EMAIL_TEMPLATE_GREETING", "안녕하세요! Sudays 서비스에 가입해주셔서 감사합니다.")
    EMAIL_TEMPLATE_INSTRUCTION = os.getenv("EMAIL_TEMPLATE_INSTRUCTION", "아래의 인증코드를 입력해주세요:")
    EMAIL_TEMPLATE_EXPIRY_NOTICE = os.getenv("EMAIL_TEMPLATE_EXPIRY_NOTICE", "인증코드 유효시간: 10분")
    EMAIL_TEMPLATE_SECURITY_NOTICE = os.getenv("EMAIL_TEMPLATE_SECURITY_NOTICE", "본인이 요청하지 않은 경우 이 메일을 무시하셔도 됩니다.")
    EMAIL_TEMPLATE_FOOTER = os.getenv("EMAIL_TEMPLATE_FOOTER", "이 메일은 Sudays 서비스에서 발송되었습니다.")
    
    # 보안 설정
    ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    ENABLE_AUTO_CLEANUP = os.getenv("ENABLE_AUTO_CLEANUP", "true").lower() == "true"
    ENABLE_EMAIL_VALIDATION = os.getenv("ENABLE_EMAIL_VALIDATION", "true").lower() == "true"
    
    # 로깅 설정
    LOG_VERIFICATION_ATTEMPTS = os.getenv("LOG_VERIFICATION_ATTEMPTS", "true").lower() == "true"
    LOG_EMAIL_SEND_RESULTS = os.getenv("LOG_EMAIL_SEND_RESULTS", "true").lower() == "true"
    
    @classmethod
    def validate_config(cls):
        """설정값 검증"""
        required_fields = [
            "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"필수 이메일 설정이 누락되었습니다: {', '.join(missing_fields)}")
        
        # 설정값 범위 검증
        if cls.VERIFICATION_CODE_LENGTH < 4 or cls.VERIFICATION_CODE_LENGTH > 8:
            raise ValueError("인증코드 길이는 4-8자 사이여야 합니다")
        
        if cls.VERIFICATION_CODE_EXPIRE_MINUTES < 1 or cls.VERIFICATION_CODE_EXPIRE_MINUTES > 60:
            raise ValueError("인증코드 유효시간은 1-60분 사이여야 합니다")
        
        if cls.MAX_VERIFICATION_ATTEMPTS < 1 or cls.MAX_VERIFICATION_ATTEMPTS > 10:
            raise ValueError("최대 인증 시도 횟수는 1-10회 사이여야 합니다")
        
        if cls.RATE_LIMIT_MINUTES < 1 or cls.RATE_LIMIT_MINUTES > 1440:
            raise ValueError("Rate Limit 시간은 1-1440분 사이여야 합니다")
    
    @classmethod
    def get_rate_limit_message(cls) -> str:
        """Rate Limit 메시지 생성"""
        return f"{cls.RATE_LIMIT_MINUTES}분 내 최대 {cls.MAX_VERIFICATION_ATTEMPTS}번까지만 인증코드를 발송할 수 있습니다"
    
    @classmethod
    def get_expiry_message(cls) -> str:
        """만료 시간 메시지 생성"""
        return f"인증코드 유효시간: {cls.VERIFICATION_CODE_EXPIRE_MINUTES}분" 