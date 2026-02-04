# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = models.py
# @Time = 2021/10/7 17:37
# @Author = xujianbo
from pydantic import BaseModel, constr, Field


class Login(BaseModel):
    username: str
    password: str


class EditFile(BaseModel):
    path: str
    content: str


"""
数据迁移命令
alembic revision --autogenerate -m "迁移脚本提示"
alembic upgrade head
"""
