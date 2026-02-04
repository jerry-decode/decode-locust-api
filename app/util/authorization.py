# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = authorization.py
# @Time = 2021/10/8 14:00
# @Author = xujianbo
import hashlib
import time
from typing import Union, Any

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.models import Login
# to get a string like this run:
# openssl rand -hex 32
from app.util.custom_exc import UserTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


class Token(BaseModel):
    access_token: str
    token_type: str


def create_token(
        subject: Union[str, Any]
) -> str:
    """
    生成token
    :param subject:
    :param expires_delta:
    :return:
    """
    # if expires_delta:
    #     expire = datetime.utcnow() + expires_delta
    # else:
    #     expire = datetime.utcnow() + timedelta(
    #         minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    #     )
    # to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(subject, SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def token_to_user(request: Request, token: OAuth2PasswordRequestForm = Depends(oauth2_scheme)):
    """
    通过token提取用户信息并校验用户是否存在
    :param request:
    :param token:
    :return:
    """
    try:
        us = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise UserTokenError()
    set_time = us.get('time')
    old_token = request.app.state.redis.get(f"{us.get('username')}")
    # 判断是否已经登录超时
    if not set_time or time.time() - float(set_time) > ACCESS_TOKEN_EXPIRE_MINUTES * 60 or token != str(old_token,
                                                                                                        encoding="utf-8"):
        raise UserTokenError()
    # 如果在一分钟内没有操作过则更新token
    if time.time() - float(set_time) > 60:
        request.app.state.redis.set(f"{us.get('username')}", token)
        request.app.state.redis.set(f"{us.get('username')}_time", time.time())
    user = Login
    user.username = us.get("username")
    user.password = us.get("password")
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验密码
    :param plain_password:
    :param hashed_password:
    :return:
    """
    return get_password_hash(plain_password) == hashed_password


def get_password_hash(password: str = 'admin12345') -> str:
    """
    生成密码
    :param password:
    :return:
    """
    m = hashlib.md5()
    m.update(password.encode("utf8"))
    return m.hexdigest()
