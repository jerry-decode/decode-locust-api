# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = api_login.py
# @Time = 2021/10/8 16:55
# @Author = xujianbo
import os
import subprocess
import time

import aiofiles
import requests
from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import JSONResponse

from app.config import ADMIN_FX
from app.schemas.user import Login
from app.util.authorization import create_token
from app.util.mysql import Db
from app.util.response_code import resp_401, resp_200

# models.ModelBase.metadata.create_all(bind=engine)

loginApp = APIRouter()


# 请求接口
@loginApp.post("/token", summary="API调试登录接口")
async def login_for_access_token(request: Request, form_data: Login = Depends(OAuth2PasswordRequestForm)):
    db_user = Db("user", "dc_user").where('email= ?', form_data.username).order(
        "created_at",
        "desc").select()
    if not db_user:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN)
    url = ADMIN_FX + "/user/admin/login"
    headers = {
        "content-type": "application/json;charset=UTF8"
    }
    json = {
        "username": form_data.username,
        "password": form_data.password
    }
    regRes = requests.post(url, headers=headers, json=json).json()
    if regRes.get("retCode") != "0":
        return regRes
    else:
        subject = {
            "username": form_data.username,
            "password": form_data.password,
            "time": time.time()
        }
        token = create_token(subject)
        request.app.state.redis.set(form_data.username, token)
        return {"access_token": token, "token_type": "bearer",
                "user": {"username": form_data.username}}


# 上传更新文件
@loginApp.post("/file/upload", summary="更新文件")
async def upload_file(request: Request, file_path: str = "/home/ubuntu/LOCUST/LOCUST_API", file: UploadFile = File(...)):
    try:
        # 获取文件名
        if not os.path.exists(file_path) or not os.path.isdir(file_path):
            return resp_401(message="原文件不存在！")
        else:
            # 删除同名旧文件
            command = f"sudo rm -rf {file_path}" if os.path.exists(
                file_path) else f"sudo rm -rf {file_path}.{file.filename}"
            subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 使用aiofiles异步写入文件
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()  # 异步读取文件内容
            await out_file.write(content)  # 异步写入文件内容
            return resp_200()
    except Exception:
        return resp_401(message="请输入正确的文件路径！")
