# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = models.py
# @Time = 2021/10/7 20:37
# @Author = xujianbo
import os
import sys

root_path = os.getcwd()
sys.path.append(root_path)

import time

import uvicorn
from fastapi import Request

from app import create_app

app = create_app()


# 计算请求时间中间件,带yield的依赖的退出部分的代码会在中间件处理完成后运行
@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
