# Sudays Backend

## 📋 프로젝트 개요

Sudays는 일기 작성 및 관리 서비스의 백엔드 API입니다. FastAPI 기반으로 구축되었으며, 이메일 인증, 회원 관리, 일기 작성 등의 기능을 제공합니다.

## 🚀 주요 기능

- **회원 관리**: 회원가입, 로그인, 이메일 인증
- **일기 관리**: 일기 작성, 조회, 수정, 삭제
- **이메일 인증**: 회원가입 전 이메일 인증 필수
- **보안**: JWT 토큰 기반 인증, 비밀번호 해싱
- **데이터베이스**: PostgreSQL 기반 데이터 저장

## 🏗️ 기술 스택

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Email**: FastAPI-Mail
- **Container**: Docker & Docker Compose
- **Server**: Gunicorn + Uvicorn
- **Language**: Python 3.8+

## 📁 프로젝트 구조

```
sudays-back/
├── app/                          # 애플리케이션 코드
│   ├── config/                   # 설정 파일
│   ├── controller/               # API 컨트롤러
│   ├── service/                  # 비즈니스 로직
│   ├── model/                    # 데이터베이스 모델
│   ├── dto/                      # 데이터 전송 객체
│   ├── util/                     # 유틸리티 함수
│   ├── dao/                      # 데이터 접근 객체
│   ├── dependencies/             # 의존성 주입
│   └── main.py                   # 애플리케이션 진입점
├── bin/                          # 서비스 관리 스크립트
│   ├── run.sh                    # 서비스 시작
│   ├── stop.sh                   # 서비스 중지
│   ├── restart.sh                # 서비스 재시작
│   └── status.sh                 # 상태 확인
├── test/                         # 테스트 코드
│   ├── test_email_verification.py
│   └── test_hash_util.py
├── env/                          # 환경 변수 파일
│   ├── local.env                 # 로컬 환경
│   ├── dev.env                   # 개발 환경
│   ├── prod.env                  # 프로덕션 환경
│   └── email.env.example         # 이메일 설정 예시
├── logs/                         # 로그 파일
├── uploads/                      # 업로드 파일
├── manage.sh                     # 서비스 관리 스크립트
├── requirements.txt              # Python 의존성
├── docker-compose.yml           # Docker 설정
└── README.md                    # 프로젝트 문서
```

## 🛠️ 설치 및 실행

### 1. 환경 요구사항

- Python 3.8+
- Docker & Docker Compose
- Git

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd sudays-back
```

### 3. 환경 설정

```bash
# 환경 변수 파일 복사
cp env/local.env.example env/local.env

# 환경 변수 편집 (이메일 설정 등)
nano env/local.env
```

### 4. 서비스 관리

`manage.sh` 스크립트를 사용하여 모든 서비스 관리가 가능합니다:

```bash
# 도움말 보기
./manage.sh

# 초기 설정
./manage.sh setup

# 의존성 설치
./manage.sh install

# 개발 모드로 시작
./manage.sh dev

# 상태 확인
./manage.sh status

# 서비스 중지
./manage.sh stop
```

## 📚 API 문서

서비스 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 서비스 관리 명령어

### 기본 명령어
```bash
./manage.sh start      # 서비스 시작
./manage.sh stop       # 서비스 중지
./manage.sh restart    # 서비스 재시작
./manage.sh status     # 상태 확인
```

### 개발 모드
```bash
./manage.sh dev        # 개발 모드로 시작
./manage.sh prod       # 프로덕션 모드로 시작
```

### 테스트
```bash
./manage.sh test           # 전체 테스트 실행
./manage.sh test-email     # 이메일 인증 테스트
```

### 설치 및 설정
```bash
./manage.sh install    # 의존성 설치
./manage.sh setup      # 초기 설정
```

### 로그 확인
```bash
./manage.sh logs           # 실시간 로그
./manage.sh logs-error     # 에러 로그
./manage.sh logs-access    # 접근 로그
```

### 정리
```bash
./manage.sh clean      # 파일 정리
./manage.sh clean-all  # 전체 정리 (주의!)
```

### Docker 관리
```bash
./manage.sh docker-up      # Docker 시작
./manage.sh docker-down    # Docker 중지
./manage.sh docker-restart # Docker 재시작
./manage.sh docker-logs    # Docker 로그
```

### 데이터베이스
```bash
./manage.sh db-migrate     # DB 마이그레이션
./manage.sh db-reset       # DB 초기화 (주의!)
```

### 이메일 인증
```bash
./manage.sh email-test     # 이메일 테스트
./manage.sh email-config   # 이메일 설정 확인
```

### 기타
```bash
./manage.sh docs       # API 문서 서버
./manage.sh info       # 시스템 정보
```

## 📧 이메일 인증 기능

### 개요
회원가입 전에 이메일 인증이 필요합니다. 인증코드 발송, 검증, 상태 확인 기능을 제공합니다.

### API 엔드포인트

#### 1. 인증코드 발송
```
POST /email/send-verification
```

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "인증코드가 이메일로 발송되었습니다",
  "email": "user@example.com",
  "expires_in_minutes": 10
}
```

#### 2. 인증코드 검증
```
POST /email/verify-code
```

**Request:**
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

**Response:**
```json
{
  "message": "이메일 인증이 완료되었습니다",
  "is_verified": true,
  "email": "user@example.com",
  "verified_at": "2024-01-01T12:00:00Z"
}
```

#### 3. 인증 상태 확인
```
GET /email/verification-status/{email}
```

**Response:**
```json
{
  "email": "user@example.com",
  "is_verified": true,
  "checked_at": "2024-01-01T12:00:00Z"
}
```

### 환경 변수 설정

`env/local.env` 파일에 다음 설정을 추가하세요:

```env
# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Verification Code Settings
VERIFICATION_CODE_LENGTH=6
VERIFICATION_CODE_EXPIRE_MINUTES=10

# Rate Limiting Settings
MAX_VERIFICATION_ATTEMPTS=3
RATE_LIMIT_MINUTES=20

# Email Template Settings
EMAIL_SUBJECT=[Sudays] 이메일 인증코드
EMAIL_TEMPLATE_TITLE=Sudays 이메일 인증
EMAIL_TEMPLATE_GREETING=안녕하세요! Sudays 서비스에 가입해주셔서 감사합니다.
EMAIL_TEMPLATE_INSTRUCTION=아래의 인증코드를 입력해주세요:
EMAIL_TEMPLATE_EXPIRY_NOTICE=인증코드 유효시간: 10분
EMAIL_TEMPLATE_SECURITY_NOTICE=본인이 요청하지 않은 경우 이 메일을 무시하셔도 됩니다.
EMAIL_TEMPLATE_FOOTER=이 메일은 Sudays 서비스에서 발송되었습니다.

# Security Settings
ENABLE_RATE_LIMITING=true
ENABLE_AUTO_CLEANUP=true
ENABLE_EMAIL_VALIDATION=true

# Logging Settings
LOG_VERIFICATION_ATTEMPTS=true
LOG_EMAIL_SEND_RESULTS=true
```

### Gmail 설정 방법
1. Gmail 계정에서 2단계 인증 활성화
2. 앱 비밀번호 생성
3. `MAIL_PASSWORD`에 앱 비밀번호 사용

## 🔐 보안 기능

### 이메일 인증
- **인증코드 유효시간**: 설정 가능 (기본 10분)
- **인증코드 길이**: 설정 가능 (기본 6자리)
- **Rate Limiting**: 설정 가능 (기본 20분 내 3회)
- **자동 정리**: 인증 완료 후 미인증 데이터 자동 삭제
- **이메일 형식 검증**: 활성화/비활성화 가능

### 비밀번호 보안
- **bcrypt 해싱**: 안전한 비밀번호 저장
- **솔트 자동 생성**: 매번 다른 솔트 사용
- **검증 기능**: 해시된 비밀번호 검증

### JWT 인증
- **토큰 기반 인증**: 안전한 사용자 인증
- **토큰 만료**: 설정 가능한 만료 시간

## 🗄️ 데이터베이스

### 주요 테이블

#### `member` 테이블
```sql
CREATE TABLE member (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `email_verification` 테이블
```sql
CREATE TABLE email_verification (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    verification_code VARCHAR(6) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_at TIMESTAMP WITH TIME ZONE
);
```

#### `diary` 테이블
```sql
CREATE TABLE diary (
    id UUID PRIMARY KEY,
    member_id UUID REFERENCES member(id),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🧪 테스트

### 테스트 실행
```bash
# 전체 테스트
./manage.sh test

# 이메일 인증 테스트
./manage.sh test-email

# 개별 테스트 파일 실행
python -m unittest test.test_hash_util
python test/test_email_verification.py
```

### 테스트 파일
- `test/test_hash_util.py`: 비밀번호 해싱 테스트
- `test/test_email_verification.py`: 이메일 인증 API 테스트

## 🐳 Docker

### 컨테이너 관리
```bash
# 컨테이너 시작
./manage.sh docker-up

# 컨테이너 중지
./manage.sh docker-down

# 컨테이너 재시작
./manage.sh docker-restart

# 로그 확인
./manage.sh docker-logs
```

### Docker Compose 설정
```yaml
services:
  postgres:
    image: postgres:latest
    container_name: my-postgres
    environment:
      POSTGRES_DB: sudays
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## 📝 로그

### 로그 파일 위치
- `logs/gunicorn.log`: Gunicorn 서버 로그
- `logs/access.log`: 접근 로그
- `logs/error.log`: 에러 로그

### 로그 확인
```bash
# 실시간 로그
./manage.sh logs

# 에러 로그
./manage.sh logs-error

# 접근 로그
./manage.sh logs-access
```

## ⚠️ 주의사항

### 위험한 명령어들
- `./manage.sh clean-all`: 모든 데이터 삭제
- `./manage.sh db-reset`: 데이터베이스 초기화

이 명령어들은 확인 후 실행됩니다.

### 환경 변수
- `env/local.env`: 로컬 개발 환경
- `env/dev.env`: 개발 환경
- `env/prod.env`: 프로덕션 환경

### Windows 환경
Windows에서는 Git Bash나 WSL을 사용하여 스크립트를 실행하세요.

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**Sudays Backend** - 안전하고 편리한 일기 서비스 🚀 