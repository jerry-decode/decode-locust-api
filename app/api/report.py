#!python3.12
# -*- coding:utf-8 -*-
# @ProjectName = DECODEEX_UI_APP
# @Time = 2025/11/18 14:27
# @Author = jerry
import os

from fastapi import Request, APIRouter, Depends
from starlette.responses import FileResponse

from app.config import REPORT_DIR
from app.util.authorization import token_to_user
from app.util.common import Common
from app.util.response_code import resp_200, resp_401

reportApp = APIRouter(dependencies=[Depends(token_to_user)])
comm = Common()


# 报告列表
@reportApp.get("/project/report/list", summary="报告列表")
async def report_list(request: Request):
    try:
        report_dir = REPORT_DIR
        if not os.path.isdir(report_dir):
            os.mkdir(report_dir)
        items = comm.get_dir(report_dir)
        for item in items:
            item["isprj"] = 1
        return resp_200(data=items)
    except Exception:
        return Exception


# 下载报告
@reportApp.get("/project/report/download", summary="下载报告")
async def download_report(request: Request, path: str):
    if os.path.isdir(path):
        # 压缩项目
        filename = path.split("/")[-1]
        name = f"{filename}.zip"
        cmd = f'cd {path.replace(f"/{filename}", "")} && sudo zip -r {name} {filename}'
        stdout, returncode = comm.execute_command(cmd)
        # 返回压缩包
        if returncode == 0:
            return FileResponse(f"{path}.zip", filename=name,
                                media_type="file/zip")
        else:
            return resp_401(message="下载失败，请重试！")
    else:
        return FileResponse(path, filename=path.split("/")[-1],
                            media_type="file/html" if path.split("/")[-1] == "csv" else "file/csv")


# 查看报告
@reportApp.get("/project/report/detail", summary="查看报告")
async def detail(request: Request, path: str):
    return FileResponse(path, filename=path.split("/")[-1])
