#!python3.12
# -*- coding:utf-8 -*-
# @ProjectName = DECODEEX_UI_APP
# @Time = 2025/11/18 14:27
# @Author = jerry
import os
from configparser import ConfigParser

from fastapi import Request, APIRouter, Depends

from app.config import PROJECT_DIR
from app.util.authorization import token_to_user
from app.util.common import Common
from app.util.response_code import resp_200, resp_401

settingApp = APIRouter(dependencies=[Depends(token_to_user)])
comm = Common()


# 项目列表
@settingApp.get("/project/setting/list", summary="配置信息列表")
async def setting_list(request: Request):
    try:
        items = []
        for item in os.listdir(PROJECT_DIR):
            if os.path.exists(f"{PROJECT_DIR}/{item}/config/locust.conf"):
                config = ConfigParser()
                conf_path = f"{PROJECT_DIR}/{item}/config/locust.conf"
                config.read(conf_path)
                nodeNum = config["works"]["works"]
                items.append(dict({"prjName": item, "nodeNum": str(nodeNum)}))
        return resp_200(data=items)
    except Exception:
        return Exception


# 设置节点个数
@settingApp.post("/setting/node/number", summary="设置节点个数")
async def set_node_num(request: Request, prj_name: str, num: str):
    try:
        config = ConfigParser()
        conf_path = f"{PROJECT_DIR}/{prj_name}/config/locust.conf"
        if not os.path.exists(conf_path):
            return resp_401(message="项目不存在!")
        config.read(conf_path)
        config["works"]["works"] = num
        with open(conf_path, 'w') as configfile:
            config.write(configfile)
        return resp_200()
    except Exception:
        return resp_401(message="参数错误!")
