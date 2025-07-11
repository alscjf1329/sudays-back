import bcrypt

class HashUtil:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호를 해시화합니다.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        입력된 비밀번호와 해시화된 비밀번호를 비교합니다.
        저장된 해시에서 자동으로 솔트를 추출하여 사용합니다.
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        ) 