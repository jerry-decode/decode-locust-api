# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = common.py
# @Time = 2021/10/14 10:55
# @Author = xujianbo
import os
import subprocess
import uuid

from pypinyin import pinyin

from app.config import PROJECT_DIR, ALLOWED_EXTENSIONS


class Common:
    def execute_command(self, command: str):
        # 使用subprocess.run来执行命令
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout, result.returncode

    def stop_locust(self, ):
        command = "docker ps | grep locust"
        stdout, returncode = self.execute_command(command)
        do_li = stdout.split("\n")
        returncode = 0
        for st in do_li:
            if st.split(" ")[0]:
                stdout, returncode = self.execute_command("docker stop " + st.split(" ")[0])
                if returncode != 0:
                    break
        return stdout, returncode

    # 获取目录树

    def get_dir(self, prj_dir):
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
                    itm = self.get_dir(path)
                if ".zip" not in item and not item.startswith("."):
                    items.append(
                        {"key": str(uuid.uuid4()), "title": item, "path": path, "parentPath": prj_dir,
                         "children": itm if itm else "",
                         "isdir": 1 if os.path.isdir(path) else 0, "isprj": 1 if prj_dir == PROJECT_DIR else 0})
        return items

    def allowed_file(self, filename: str) -> bool:
        """
        检查文件扩展名是否在允许的扩展名集合中
        """
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
