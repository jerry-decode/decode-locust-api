#!python3.7
# -*- coding:utf-8 -*-

# @ProjectName = 'fastapi'
# @Author = 'xujianbo'
# @Time = '2020/11/12 16:18'
"""
定义返回的状态

# 看到文档说这个orjson 能压缩性能(squeezing performance)
https://fastapi.tiangolo.com/advanced/custom-response/#use-orjsonresponse

It's possible that ORJSONResponse might be a faster alternative.

# 安装
pip install --upgrade orjson

测试了下，序列化某些特殊的字段不友好，比如小数
TypeError: Type is not JSON serializable: decimal.Decimal
"""
import json
from datetime import datetime
from typing import Union

from fastapi import status
from fastapi.responses import JSONResponse, Response  # , ORJSONResponse


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
        data = json.loads(json.dumps(de, cls=DateEncoder))
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


def resp_200(*, data: Union[list, dict, str] = None) -> Response:
    data = __jsonStr__(data)
    if isinstance(data, list):
        data = {
            "items": data
        }
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'retCode': 200,
            'msg': "操作成功！",
            'data': data,
            'status': True,
        }
    )


def resp_401(*, data: str = None, message: str = "BAD REQUEST") -> Response:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'retCode': 400,
            'retMsg': message,
            'data': data,
            'status': False,
        }
    )


def resp_403(*, data: str = None, message: str = "Forbidden") -> Response:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            'retCode': 403,
            'retMsg': message,
            'data': data,
            'status': False,
        }
    )


def resp_404(*, data: str = None, message: str = "Page Not Found") -> Response:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'retCode': 404,
            'retMsg': message,
            'data': data,
            'status': False,
        }
    )


def resp_422(*, data: str = None, message: Union[list, dict, str] = "UNPROCESSABLE_ENTITY") -> Response:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'retCode': 422,
            'retMsg': message,
            'data': data,
            'status': False,
        }
    )


def resp_500(*, data: str = None, message: Union[list, dict, str] = "Server Internal Error") -> Response:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'retCode': "500",
            'retMsg': message,
            'data': data,
            'status': False,
        }
    )


# 自定义
def resp_5000(*, data: Union[list, dict, str] = None, message: str = "Token failure") -> Response:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            'retCode': 5000,
            'retMsg': message,
            'data': data,
            'status': False,
        }
    )


def resp_5001(*, data: Union[list, dict, str] = None, message: str = "User Not Found") -> Response:
    data = __jsonStr__(data)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            'retCode': 5001,
            'retMsg': message,
            'data': data,
            'status': False,
        }
    )
