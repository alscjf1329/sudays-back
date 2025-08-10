#!/usr/bin/env python3
"""
이메일 인증 기능 테스트 스크립트
"""

import requests

# 서버 URL (개발 환경)
BASE_URL = "http://localhost:8000"

def test_email_verification():
    """이메일 인증 기능 테스트"""
    
    # 테스트용 이메일 (실제 이메일로 변경하세요)
    test_email = "test@example.com"
    
    print("=== 이메일 인증 기능 테스트 ===")
    
    # 1. 인증코드 발송 테스트
    print("\n1. 인증코드 발송 테스트")
    try:
        response = requests.post(
            f"{BASE_URL}/verify/send/email/verification-code",
            json={"email": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ 인증코드 발송 성공")
            print(f"응답: {response.json()}")
        else:
            print(f"❌ 인증코드 발송 실패: {response.status_code}")
            print(f"오류: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")
        return
    
    # 2. 인증 상태 확인 테스트
    print("\n2. 인증 상태 확인 테스트")
    try:
        response = requests.get(f"{BASE_URL}/verify/check-verification/{test_email}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 인증 상태 확인 성공")
            print(f"응답: {result}")
        else:
            print(f"❌ 인증 상태 확인 실패: {response.status_code}")
            print(f"오류: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")
    
    # 3. 잘못된 인증코드로 검증 테스트
    print("\n3. 잘못된 인증코드 검증 테스트") 
    try:
        response = requests.post(
            f"{BASE_URL}/verify/code",
            json={
                "email": test_email,
                "verification_code": "000000"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 잘못된 인증코드 처리 성공")
            print(f"응답: {response.json()}")
        else:
            print(f"❌ 잘못된 인증코드 처리 실패: {response.status_code}")
            print(f"오류: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")

def test_signup_without_verification():
    """미인증 상태로 회원가입 테스트"""
    
    print("\n=== 미인증 상태로 회원가입 테스트 ===")
    
    test_email = "unverified@example.com"
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": test_email,
                "password": "TestPassword123!",
                "nickname": "testuser"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            result = response.json()
            if "이메일 인증이 필요합니다" in result.get("detail", ""):
                print("✅ 미인증 상태 회원가입 차단 성공")
                print(f"응답: {result}")
            else:
                print(f"❌ 예상과 다른 오류: {result}")
        else:
            print(f"❌ 미인증 상태 회원가입 차단 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")

if __name__ == "__main__":
    print("이메일 인증 기능 테스트를 시작합니다...")
    print("주의: 실제 이메일 주소로 테스트하려면 test_email 변수를 수정하세요.")
    print("서버가 실행 중인지 확인하세요.")
    
    # 테스트 실행
    test_email_verification()
    test_signup_without_verification()
    
    print("\n=== 테스트 완료 ===") 