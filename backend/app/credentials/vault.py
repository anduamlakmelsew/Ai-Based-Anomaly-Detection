import base64
from cryptography.fernet import Fernet


class CredentialVault:

    def __init__(self, key):
        self.fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        encrypted = self.fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt(self, value: str) -> str:
        decoded = base64.b64decode(value.encode())
        decrypted = self.fernet.decrypt(decoded)
        return decrypted.decode()