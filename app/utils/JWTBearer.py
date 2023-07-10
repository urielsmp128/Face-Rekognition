from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.auth import AuthHandler
from app.utils.errors_handler import responses


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                return responses[403]
            if not self.verify_jwt(credentials.credentials):
                return responses[403]
            return credentials.credentials
        else:
            return responses[403]

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = AuthHandler.decode_token(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
