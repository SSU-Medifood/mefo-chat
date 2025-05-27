from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False) 

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials or not credentials.scheme.lower() == "bearer":
        raise HTTPException(status_code=401, detail="Authorization 헤더가 필요합니다.")
    return credentials.credentials
