from passlib.context import CryptContext


class Secure:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password(self, password: str) -> str:
        return self.password_context.hash(password)

    def verify_password(self, password: str, hashed_pass: str) -> bool:
        return self.password_context.verify(password, hashed_pass)
