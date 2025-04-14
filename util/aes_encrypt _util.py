import base64
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class AESEncryptUtil:
    AES_ENCRYPTION_KEY = os.getenv('AES_ENCRYPTION_KEY')
    if not AES_ENCRYPTION_KEY:
        raise ValueError("AES_ENCRYPTION_KEY 환경변수가 설정되지 않았습니다.")

    @staticmethod
    def encrypt(data: str) -> str:
        """
        문자열을 AES로 암호화합니다.
        
        Args:
            data: 암호화할 문자열
            
        Returns:
            암호화된 문자열 (base64 인코딩)
        """
        cipher = AES.new(AESEncryptUtil.AES_ENCRYPTION_KEY, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return f"{iv}:{ct}"

    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """
        AES로 암호화된 문자열을 복호화합니다.
        
        Args:
            encrypted_data: 암호화된 문자열 (iv:ciphertext 형식)
            
        Returns:
            복호화된 원본 문자열
        """
        iv, ct = encrypted_data.split(':')
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        
        cipher = AES.new(AESEncryptUtil.AES_ENCRYPTION_KEY, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
