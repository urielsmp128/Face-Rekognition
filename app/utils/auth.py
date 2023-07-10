import jwt
from datetime import datetime, timedelta

from app.utils.errors_handler import responses
from app.utils.config import settings

SECRET = settings.SECRET
TOKEN_EXP = int(settings.TOKEN_EXP_TIME)
TOKEN_EXP_REC = int(settings.TOKEN_EXP_TIME_RESET_PASSWORD)
ALGORITHM = "HS256"


class AuthHandler:
    def encode_token(self, email):
        if "@" in email:
            payload = {
                "exp": datetime.utcnow()
                + timedelta(days=TOKEN_EXP, minutes=0),
                "sub": email,
            }
            return jwt.encode(payload, SECRET, ALGORITHM)
        else:
            payload = {
                "exp": datetime.utcnow()
                + timedelta(days=0, minutes=TOKEN_EXP_REC),
                "sub": email,
            }
            return jwt.encode(payload, SECRET, ALGORITHM)

    def decode_token(self, token):
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        if payload:
            return payload["sub"]
        return responses[401]
