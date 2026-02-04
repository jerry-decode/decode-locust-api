# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = users.py
# @Time = 2022/1/9 19:45
# @Author = xujianbo
from pydantic import BaseModel, constr, Field, conint


class User(BaseModel):
    username: constr(max_length=30) = Field(..., title="登录账号")
    password: constr(max_length=40) = Field(..., title="登录密码")
    role: conint() = Field(None, title="角色")


class UpdatePassword(BaseModel):
    userId: constr(max_length=32) = Field(..., title="账号id")
    oldPasseord: constr(max_length=40) = Field(..., title="旧密码")
    newPasseord: constr(max_length=40) = Field(..., title="新密码")


class Login(BaseModel):
    username: constr(max_length=30) = Field(..., title="登录账号", description="登录账号")
    password: constr(max_length=30) = Field(..., title="登录密码", description="登录密码")


class Edit(User):
    id: constr(max_length=32, min_length=32) = Field(..., title="用户ID")
