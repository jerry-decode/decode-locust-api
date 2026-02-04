#!python3.12
# -*- coding:utf-8 -*-
# @ProjectName = DECODEEX_UI_APP
# @Time = 2025/11/18 11:36
# @Author = jerry
import os
import time
from configparser import ConfigParser

import aiofiles
import requests
from fastapi import APIRouter, Request, UploadFile, File, Depends
from starlette.responses import FileResponse

from app.config import PROJECT_DIR, REPORT_DIR
from app.models.models import EditFile
from app.util.authorization import token_to_user
from app.util.common import Common
from app.util.response_code import resp_200, resp_401

projectApp = APIRouter(dependencies=[Depends(token_to_user)])

comm = Common()


@projectApp.post("/servers/start", summary="启动服务")
async def start_server(request: Request, prj_dir: str):
    config = ConfigParser()
    conf_path = f"{PROJECT_DIR}/{prj_dir}/config/locust.conf"
    config.read(conf_path)
    num = config['works']['works']
    command = [f"cd {PROJECT_DIR}/{prj_dir}/docker && sudo docker-compose up --scale worker={num} -d"]
    try:
        comm.stop_locust()
        stdout, returncode = comm.execute_command(command)
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return Exception


# 重启服务
@projectApp.post("/servers/restart", summary="重启服务")
async def restart_server(request: Request):
    try:
        # stop_locust()
        command = ["sudo docker-compose restart"]
        stdout, returncode = comm.execute_command(command)
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return Exception


# 停止服务
@projectApp.post("/servers/stop", summary="停止服务")
async def stop_server(request: Request, prj_dir: str):
    try:
        # stop_locust()
        command = [f"cd {PROJECT_DIR}/{prj_dir}/docker && sudo docker-compose stop"]
        stdout, returncode = comm.execute_command(command)
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return Exception


# 校验服务是否启动
@projectApp.get("/servers/check", summary="校验服务是否启动")
async def check_server(request: Request):
    try:
        command = "sudo docker ps | grep locust"
        stdout, returncode = comm.execute_command(command)
        do_li = stdout.split("\n")
        if do_li and do_li[0]:
            return resp_200()
        else:
            return resp_401(message="请先启动服务！")
    except Exception:
        return Exception


# 停止所有服务
@projectApp.post("/servers/stop/all", summary="停止所有服务")
async def stop_all(request: Request):
    try:
        stdout, returncode = comm.stop_locust()
        if returncode == 0:
            return resp_200()
        else:
            return resp_401(message=stdout)
    except Exception:
        return resp_401(message="执行失败，请重试！")


# 项目列表
@projectApp.get("/project/list", summary="项目列表")
async def project_list(request: Request, file_name: str = ""):
    try:
        prj_dir = PROJECT_DIR if not file_name else file_name
        if not os.path.exists(prj_dir):
            return resp_401(message="文件不存在！")
        items = comm.get_dir(prj_dir)
        items = [item for item in items if
                 os.path.isdir(item["path"]) and item["title"] not in ["__pycache__", "reports"]]
        return resp_200(data=items)
    except Exception:
        return Exception


# 删除文件
@projectApp.post("/project/file/delete", summary="删除文件")
async def delete_file(request: Request, file_path: str, ):
    if os.path.exists(file_path):
        # 删除同名旧文件
        command = f"sudo rm -rf {file_path}"
        comm.execute_command(command)
        return resp_200()
    else:
        resp_401(message="文件不存在！")


# 文件详情
@projectApp.get("/project/file/detail", summary="文件详情")
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
@projectApp.post("/project/file/edit", summary="修改文件")
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
@projectApp.post("/project/file/upload", summary="更新文件")
async def upload_file(request: Request, file_path: str, file: UploadFile = File(...)):
    try:
        # 获取文件名
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return resp_401(message="原文件不存在！")
        else:
            # 删除同名旧文件
            command = f"sudo rm -rf {file_path}.*"
            comm.execute_command(command)
        # 使用aiofiles异步写入文件
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()  # 异步读取文件内容
            await out_file.write(content)  # 异步写入文件内容
            return resp_200()
    except Exception:
        return resp_401(message="请输入正确的文件路径！")


# 上传更新文件
@projectApp.post("/project/file/add", summary="添加文件")
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


# 上传项目
@projectApp.post("/project/upload", summary="上传项目")
async def add_project(file: UploadFile = File(...)):
    # 获取文件名
    filename = file.filename
    re = comm.allowed_file(filename)
    if not re:
        return resp_401(message="文件格式不正确！")
    # def upload():
    # 删除同名旧文件
    command = f"cd {PROJECT_DIR} && sudo rm -rf {filename.split('.')[0]}.*"
    comm.execute_command(command)
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
        comm.execute_command(command)
        # 删除压缩包
        command = f"cd {PROJECT_DIR} && sudo rm -rf {filename} && sudo chmod 777 {PROJECT_DIR}/{filename.split('.')[0]}/config/locust.conf && cd {PROJECT_DIR}/{filename.split('.')[0]}/docker && docker-compose build"
        comm.execute_command(command)
        return resp_200()
    # #创建线程对象
    # t = threading.Thread(target = upload())
    # t.setDaemon(True)
    # t.start()
    # t.join()


# 下载项目
@projectApp.get("/project/download", summary="下载项目")
async def download_project(request: Request, path: str):
    try:
        if not os.path.exists(path):
            return resp_401(message="项目不存在")
        # 压缩项目
        filename = path.split("/")[-1]
        cmd = f'cd {path.replace(f"/{filename}", "")} && sudo zip -r {filename}.zip {filename}'
        stdout, returncode = comm.execute_command(cmd)
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
@projectApp.post("/project/report/save", summary="保存报告")
async def save_project(request: Request, prj_name: str, rep_name: str = ""):
    try:
        if not rep_name:
            timestamp = time.time() + 8 * 3600
            name = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(timestamp))
        else:
            name = rep_name
        # 创建报告文件夹
        file_location = REPORT_DIR
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
            file_name = f'{path_report}/{ads.split("/")[-2]}.csv' if ads.split("/")[
                                                                         -1] == "csv" else f"{path_report}/report.html"
            open(file_name, 'wb').write(report.content)
        return resp_200()
    except Exception:
        return resp_401(message="请压测完成后再保存报告！")
