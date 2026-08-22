"""Sign up and sign in.

Nickname + email + password, nothing else. No student ID, no real name: the
forum is worth more with a low barrier than with a verified roster.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: EmailStr
    nickname: str = Field(min_length=2, max_length=48)
    password: str = Field(min_length=8, max_length=128)


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


def _me(user: User) -> dict:
    return {
        "id": user.id,
        "nickname": user.nickname,
        "email": user.email,
        "is_admin": user.is_admin,
    }


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(payload: SignUpRequest, db: Session = Depends(get_db)) -> dict:
    existing = db.scalar(
        select(User).where(or_(User.email == payload.email, User.nickname == payload.nickname))
    )
    if existing:
        raise HTTPException(409, "That email or nickname is already registered")
    user = User(
        email=str(payload.email),
        nickname=payload.nickname,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    return {"token": create_access_token(str(user.id)), "user": _me(user)}


@router.post("/signin")
def sign_in(payload: SignInRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Wrong email or password")
    if not user.is_active:
        raise HTTPException(403, "This account is suspended")
    return {"token": create_access_token(str(user.id)), "user": _me(user)}


@router.get("/me")
def me(user: User = Depends(current_user)) -> dict:
    return _me(user)
