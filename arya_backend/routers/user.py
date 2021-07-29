from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from arya_backend.auth import create_access_token, verify_password
from arya_backend.db.user import User
from arya_backend.dependencies import get_current_user
from arya_backend.models import MessageModel
from arya_backend.models.auth import SignInUser, Token

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User().get(form_data.username)
    if (not user) or (not verify_password(form_data.password, user["hashed_password"])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": " ".join(user["scopes"])}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/",
    responses={
        status.HTTP_200_OK: {"model": MessageModel},
        status.HTTP_201_CREATED: {"model": MessageModel},
    },
)
async def signin(payload: SignInUser, user_db: User = Depends()):
    user = user_db.create(payload.username, payload.password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"error": "User alredy exists."}
        )
    else:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"data": "OK"})


@router.get("/", responses={status.HTTP_200_OK: {"model": MessageModel}})
async def get_me(user=Depends(get_current_user)):
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": user.username})
