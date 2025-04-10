import unittest
from util.hash_util import HashUtil

class TestHashUtil(unittest.TestCase):
    def test_hash_password(self):
        # 테스트용 비밀번호
        password = "test1234"
        
        # 비밀번호 해싱
        hashed_password = HashUtil.hash_password(password)
        
        # 해시된 비밀번호가 문자열인지 확인
        self.assertIsInstance(hashed_password, str)
        # 해시된 비밀번호가 원본과 다른지 확인
        self.assertNotEqual(password, hashed_password)
        
    def test_verify_password(self):
        # 테스트용 비밀번호
        password = "test1234"
        
        # 비밀번호 해싱
        hashed_password = HashUtil.hash_password(password)
        
        # 올바른 비밀번호 검증
        self.assertTrue(HashUtil.verify_password(password, hashed_password))
        
        # 잘못된 비밀번호 검증
        wrong_password = "wrong1234"
        self.assertFalse(HashUtil.verify_password(wrong_password, hashed_password))
        
    def test_different_salts(self):
        # 같은 비밀번호를 두 번 해싱했을 때 다른 해시가 생성되는지 확인
        password = "test1234"
        
        hashed1 = HashUtil.hash_password(password)
        hashed2 = HashUtil.hash_password(password)
        
        # 서로 다른 솔트가 사용되어 다른 해시가 생성되어야 함
        self.assertNotEqual(hashed1, hashed2)
        
        # 두 해시 모두 원본 비밀번호로 검증 가능해야 함
        self.assertTrue(HashUtil.verify_password(password, hashed1))
        self.assertTrue(HashUtil.verify_password(password, hashed2))

if __name__ == '__main__':
    unittest.main() 