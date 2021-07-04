from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from arya_backend.auth import decode_access_token
from arya_backend.db.user import get as get_user
from arya_backend.models.auth import User

scopes = {"qa:add": "add qa"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", scopes=scopes)


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    token_data = decode_access_token(token, credentials_exception)
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
