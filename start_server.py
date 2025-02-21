# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = api_login.py
# @Time = 2024/12/29 09:55
# @Author = jerry
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Union, List

import requests
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import aiofiles
import uvicorn
import uuid
from fastapi import APIRouter, Request, FastAPI, UploadFile, File
from pydantic import BaseModel, constr, Field, AnyHttpUrl
from starlette import status
from starlette.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from configparser import ConfigParser

PROJECT_DIR = os.getcwd()

if not os.path.exists(PROJECT_DIR):
    os.mkdir(PROJECT_DIR)
locust_app = APIRouter()
BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['*']


def register_cors(app: FastAPI):
    """
    支持跨域

    貌似发现了一个bug
    https://github.com/tiangolo/fastapi/issues/133

    :param app:
    :return:
    """
    if BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


def __jsonStr__(data: Union[list, dict, str, type]):
    if isinstance(data, list):
        de = []
        for i in data:
            try:
                de.append(i.to_dict())
            except:
                de.append(i)
        data = json.loads(json.dumps(de))
    else:
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list):
                    de = []
                    for i in v:
                        try:
                            if isinstance(i, dict):
                                for key, value in i.items():
                                    if isinstance(value, list):
                                        li = []
                                        for va in value:
                                            li.append(va.to_dict())
                                        i[key] = li
                            de.append(i.to_dict())
                        except:
                            de.append(i)
                    data[k] = de
        data = json.loads(json.dumps(data, cls=DateEncoder))
    return data


class EditFile(BaseModel):
    path: str
    content: str


# 获取目录树
def get_dir(prj_dir):
    # 获取当前目录下的所有文件和文件夹
    flli = os.listdir(prj_dir)
    # if not file_name:
    #     # 过滤出文件夹
    #     flli = [item for item in flli if os.path.isdir(os.path.join(PROJECT_DIR, item)) and not "." in item]
    items = []
    for item in flli:
        if item not in ["__pycache__", ".git", "venv"] and ("." not in item or os.path.isfile(f"{prj_dir}/{item}")):
            itm = []
            path = f"{prj_dir}/{item}"
            if os.path.isdir(path):
                itm = get_dir(path)
            if ".zip" not in item and not item.startswith("."):
                items.append(
                    {"key": str(uuid.uuid4()), "title": item, "path": path, "parentPath": prj_dir,
                     "children": itm if itm else "",
                     "isdir": 1 if os.path.isdir(path) else 0, "isprj": 1 if prj_dir == PROJECT_DIR else 0})
    return items


def resp_200(*, data: Union[list, dict, str] = None) -> JSONResponse:
    data = __jsonStr__(data)
    if isinstance(data, list):
        data = {
            "items": data
        }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': 200,
            'msg': "操作成功！",
            'data': data,
            'status': True,
        }
    )


def resp_401(*, data: str = None, message: str = "BAD REQUEST") -> JSONResponse:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': 400,
            'msg': message,
            'data': data,
            'status': False,
        }
    )


# 执行cmd命令
def execute_command(command: str):
    # 使用subprocess.run来执行命令
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout, result.returncode


# 上传的文件格式
ALLOWED_EXTENSIONS = {"rar", "zip", "gz", "tgz", "xz", "bz2"}


class Login(BaseModel):
    username: constr(max_length=30) = Field(..., title="登录账号", description="登录账号")
    password: constr(max_length=30) = Field(..., title="登录密码", description="登录密码")


# 校验允许上传的文件
def allowed_file(filename: str) -> bool:
    """
    检查文件扩展名是否在允许的扩展名集合中
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 停止locust服务
def stop_locust():
    command = "docker ps | grep locust"
    stdout, returncode = execute_command(command)
    do_li = stdout.split("\n")
    returncode = 0
    for st in do_li:
        if st.split(" ")[0]:
            stdout, returncode = execute_command("docker stop " + st.split(" ")[0])
            if returncode != 0:
                break
    return stdout, returncode


# 登录
@locust_app.post("/login", summary="登录")
async def login(request: Request, userInfo: Login):
    try:
        url = "https://decodeex-api.dev.decodebackoffice.com/user/admin/login"
        data = {
            "username": userInfo.username,
            "password": userInfo.password
        }
        res = requests.post(url, json=data).json()
        if res["retCode"] == "0":
            data = {"access_token": "sfsdfsdfgsdsdggsgsdfgadsfgsdg", "token_type": "bearer"}
            return resp_200(data=data)
        else:
            return resp_401(message="账号或者密码错误！")
    except Exception:
        return Exception


@locust_app.post("/servers/start", summary="启动服务")
async def start_server(request: Request, prj_dir: str):
    config = ConfigParser()
    conf_path = f"{PROJECT_DIR}/{prj_dir}/config/locust.conf"
    config.read(conf_path)
    num = config['works']['works']
    command = [f"cd {PROJECT_DIR}/{prj_dir}/docker && sudo docker-compose up --scale worker={num} -d"]
    try:
        stop_locust()
        stdout, returncode = execute_command(command)
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return Exception


# 重启服务
@locust_app.post("/servers/restart", summary="重启服务")
async def restart_server(request: Request):
    try:
        # stop_locust()
        command = ["sudo docker-compose restart"]
        stdout, returncode = execute_command(command)
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return Exception


# 停止服务
@locust_app.post("/servers/stop", summary="停止服务")
async def stop_server(request: Request, prj_dir: str):
    try:
        # stop_locust()
        command = [f"cd {PROJECT_DIR}/{prj_dir}/docker && sudo docker-compose stop"]
        stdout, returncode = execute_command(command)
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return Exception


# 校验服务是否启动
@locust_app.get("/servers/check", summary="校验服务是否启动")
async def check_server(request: Request):
    try:
        command = "sudo docker ps | grep locust"
        stdout, returncode = execute_command(command)
        do_li = stdout.split("\n")
        if do_li and do_li[0]:
            return resp_200()
        else:
            return resp_401(message="请先启动服务！")
    except Exception:
        return Exception


# 停止所有服务
@locust_app.post("/servers/stop/all", summary="停止所有服务")
async def stop_all(request: Request):
    try:
        stdout, returncode = stop_locust()
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return resp_401(message="执行失败，请重试！")


# 项目列表
@locust_app.get("/project/list", summary="项目列表")
async def project_list(request: Request, file_name: str = ""):
    try:
        prj_dir = PROJECT_DIR if not file_name else file_name
        if not os.path.exists(prj_dir):
            return resp_401(message="文件不存在！")
        items = get_dir(prj_dir)
        items = [item for item in items if
                 os.path.isdir(item["path"]) and item["title"] not in ["__pycache__", "reports"]]
        return resp_200(data=items)
    except Exception:
        return Exception


# 删除文件
@locust_app.post("/project/file/delete", summary="删除文件")
async def delete_file(request: Request, file_path: str, ):
    if os.path.exists(file_path):
        # 删除同名旧文件
        command = f"sudo rm -rf {file_path}"
        execute_command(command)
        return resp_200()
    else:
        resp_401(message="文件不存在！")


# 文件详情
@locust_app.get("/project/file/detail", summary="文件详情")
async def file_detail(request: Request, path: str = ""):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as file:
                content = file.read()  # 读取文件内容
            return resp_200(data=content)
        else:
            return resp_401(message=f"{path}文件不存在!")
    except Exception:
        return Exception


# 修改文件
@locust_app.post("/project/file/edit", summary="修改文件")
async def edit_file(request: Request, data: EditFile):
    try:
        if os.path.exists(data.path):
            # 使用aiofiles异步写入文件
            with open(data.path, "w") as file:
                file.write(data.content)  # 异步写入文件内容
                return resp_200()
        else:
            return resp_401(message="请输入正确的文件路径！")
    except Exception:
        return Exception


# 上传更新文件
@locust_app.post("/project/file/upload", summary="更新文件")
async def upload_file(request: Request, file_path: str, file: UploadFile = File(...)):
    try:
        # 获取文件名
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return resp_401(message="原文件不存在！")
        else:
            # 删除同名旧文件
            command = f"sudo rm -rf {file_path}.*"
            execute_command(command)
        # 使用aiofiles异步写入文件
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()  # 异步读取文件内容
            await out_file.write(content)  # 异步写入文件内容
            return resp_200()
    except Exception:
        return resp_401(message="请输入正确的文件路径！")


# 上传更新文件
@locust_app.post("/project/file/add", summary="添加文件")
async def add_file(request: Request, file_path: str, file: UploadFile = File(...)):
    try:
        filename = file.filename
        file_location = os.path.join(file_path, filename)
        # 获取文件名
        if not os.path.isdir(file_path):
            return resp_401(message="文件路径不存在！")
        # 使用aiofiles异步写入文件
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()  # 异步读取文件内容
            await out_file.write(content)  # 异步写入文件内容
            return resp_200()
    except Exception:
        return resp_401(message="请输入正确的文件路径！")


# 项目列表
@locust_app.get("/project/setting/list", summary="配置信息列表")
async def setting_list(request: Request):
    try:
        items = []
        for item in os.listdir(PROJECT_DIR):
            if "LOCUST" in item and os.path.exists(f"{PROJECT_DIR}/{item}/config/locust.conf"):
                config = ConfigParser()
                conf_path = f"{PROJECT_DIR}/{item}/config/locust.conf"
                config.read(conf_path)
                nodeNum = config["works"]["works"]
                items.append(dict({"prjName": item, "nodeNum": str(nodeNum)}))
        return resp_200(data=items)
    except Exception:
        return Exception


# 设置节点个数
@locust_app.post("/setting/node/number", summary="设置节点个数")
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


# 上传项目
@locust_app.post("/project/upload", summary="上传项目")
async def add_project(file: UploadFile = File(...)):
    # 获取文件名
    filename = file.filename
    re = allowed_file(filename)
    if not re:
        return resp_401(message="文件格式不正确！")
    # def upload():
    # 删除同名旧文件
    command = f"cd {PROJECT_DIR} && sudo rm -rf {filename.split('.')[0]}.*"
    execute_command(command)
    file_location = os.path.join(PROJECT_DIR, filename)
    # # 使用shutil将上传的文件复制到指定目录
    # with open(file_location, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    # 使用aiofiles异步写入文件
    async with aiofiles.open(file_location, 'wb') as out_file:
        content = await file.read()  # 异步读取文件内容
        await out_file.write(content)  # 异步写入文件内容
        # 解压缩文件
        if "zip" in filename:
            command = f"cd {PROJECT_DIR} && unzip {filename}"
        elif "rar" in filename:
            command = f"cd {PROJECT_DIR} && unrar x {filename}"
        else:
            command = f"cd {PROJECT_DIR} && tar -xvf {filename}"
        time.sleep(2)
        execute_command(command)
        # 删除压缩包
        command = f"cd {PROJECT_DIR} && sudo rm -rf {filename} && sudo chmod 777 {PROJECT_DIR}/{filename.split('.')[0]}/config/locust.conf"
        execute_command(command)
        return resp_200()
    # #创建线程对象
    # t = threading.Thread(target = upload())
    # t.setDaemon(True)
    # t.start()
    # t.join()


# 下载项目
@locust_app.get("/project/download", summary="下载项目")
async def download_project(request: Request, path: str):
    try:
        if not os.path.exists(path):
            return resp_401(message="项目不存在")
        # 压缩项目
        filename = path.split("/")[-1]
        cmd = f"cd {path.replace(f"/{filename}", "")} && sudo zip -r {filename}.zip {filename}"
        stdout, returncode = execute_command(cmd)
        # 返回压缩包
        if returncode == 0:
            return FileResponse(f"{path}.zip", filename=f"{filename}.zip",
                                media_type="file/zip")
        else:
            return resp_401(message="下载失败，请重试！")
    except Exception:
        return resp_401(message="下载失败，请重试！")
    # # 清理压缩包
    # finally:
    #     time.sleep(30)
    #     cmd = f"cd {path.replace(f"/{filename}", "")} && sudo rm -rf {filename}.zip"
    #     execute_command(cmd)


# 保存报告
@locust_app.post("/project/report/save", summary="保存报告")
async def save_project(request: Request, prj_name: str, rep_name: str = ""):
    try:
        if not rep_name:
            timestamp = time.time() + 8 * 3600
            name = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(timestamp))
        else:
            name = rep_name
        # 创建报告文件夹
        file_location = f"{PROJECT_DIR}/reports"
        if not os.path.isdir(file_location):
            os.mkdir(file_location)
            # execute_command(f"sudo mkdir {file_location}")
        path_report = f"{file_location}/{prj_name}_reports"
        if not os.path.isdir(path_report):
            # execute_command(f"sudo mkdir {path_report}")
            os.mkdir(path_report)
        path_report = f"{file_location}/{prj_name}_reports/{name}"
        if not os.path.isdir(path_report):
            # execute_command(f"sudo mkdir {path_report}")
            os.mkdir(path_report)
        # 保存报告
        address = ["/stats/report?download=1&theme=dark", "/exceptions/csv", "/stats/failures/csv",
                   "/stats/requests/csv"]
        for ads in address:
            report = requests.get(f"http://127.0.0.1:8089{ads}")
            file_name = f"{path_report}/{ads.split("/")[-2]}.csv" if ads.split("/")[
                                                                         -1] == "csv" else f"{path_report}/report.html"
            open(file_name, 'wb').write(report.content)
        return resp_200()
    except Exception:
        return resp_401(message="请压测完成后再保存报告！")


# 报告列表
@locust_app.get("/project/report/list", summary="报告列表")
async def report_list(request: Request):
    try:
        report_dir = f"{PROJECT_DIR}/reports"
        if not os.path.isdir(report_dir):
            os.mkdir(report_dir)
        items = get_dir(report_dir)
        for item in items:
            item["isprj"] = 1
        return resp_200(data=items)
    except Exception:
        return Exception


# 下载报告
@locust_app.get("/project/report/download", summary="下载报告")
async def download_report(request: Request, path: str):
    if os.path.isdir(path):
        # 压缩项目
        filename = path.split("/")[-1]
        name = f"{filename}.zip"
        cmd = f"cd {path.replace(f"/{filename}", "")} && sudo zip -r {name} {filename}"
        stdout, returncode = execute_command(cmd)
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
@locust_app.get("/project/report/detail", summary="查看报告")
async def detail(request: Request, path: str):
    return FileResponse(path, filename=path.split("/")[-1])


def create_app():
    """
    生成FastAPI对象
    :return:
    """
    app = FastAPI(title="LOCUST服务", version="1.0", description="")
    app.include_router(locust_app, prefix='/api', tags=['LOCUST服务'])
    app.mount("/reports", StaticFiles(directory="reports", html=True), name="reports")
    # 跨域设置
    register_cors(app)
    return app


app = create_app()
if __name__ == '__main__':
    uvicorn.run('start_server:app', host='127.0.0.1', port=8000, reload=True)
