#!python3.12
# -*- coding:utf-8 -*-
# @ProjectName = DECODEEX_UI_APP
# @Time = 2025/11/18 11:32
# @Author = jerry
import time

import requests
from fastapi import APIRouter, Request

from app.config import ADMIN_FX
from app.models.models import Login
from app.util.authorization import create_token
from app.util.response_code import resp_5001, resp_200

userApp = APIRouter()


# 登录-------此处需要改造
@userApp.post("/login", summary="登录")
async def login(request: Request, userInfo: Login):
    # db_user = Db("user", "dc_user").where('email= ?', userInfo.username).order(
    #     "created_at",
    #     "desc").select()
    # if not db_user:
    #     return resp_5001(message="用户不存在！")
    url = ADMIN_FX + "/user/admin/login"
    headers = {
        "content-type": "application/json;charset=UTF8"
    }
    json = {
        "username": userInfo.username,
        "password": userInfo.password
    }
    regRes = requests.post(url, headers=headers, json=json).json()
    result = regRes["result"]
    if regRes.get("retCode") != "0":
        return resp_5001(message=regRes)
    else:
        subject = {
            "username": userInfo.username,
            "password": userInfo.password,
            "time": time.time()
        }
        token = create_token(subject)
        request.app.state.redis.set(userInfo.username, token)
        data = {"access_token": token, "token_type": "bearer",
                "accountStatus": result["accountStatus"], "createdAt": result["createdAt"],
                "mobile": result["mobile"],
                "name": result["name"], "email": result["email"]}
        return resp_200(data=data)
