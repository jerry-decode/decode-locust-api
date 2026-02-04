# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @ProjectName = fastapi_test
# @FileName = authorization.py
# @Time = 2021/10/10 12:10
# @Author = xujianbo

import requests


class Request:

    @classmethod
    def get(cls, url, transfer_mode="params", data=None, headers=None):
        """
        执行get请求
        :param url: 请求地址
        :param transfer_mode: 参数传递方式
        :param data: 参数
        :param headers: header值
        :return:
        """
        if transfer_mode == "form":
            res = requests.session().get(url, data=data, headers=headers)
            return res
        else:
            res = requests.session().get(url, params=data, headers=headers)
            return res

    @classmethod
    def post(cls, url, transfer_mode="body", data=None, headers=None):
        """
        执行get请求
        :param url: 请求地址
        :param transfer_mode: 参数传递方式
        :param data: 参数
        :param headers: header值
        :return:
        """
        if transfer_mode == "body":
            res = requests.session().post(url, json=data, headers=headers)
            return res
        elif transfer_mode == "params":
            return requests.session().post(url, params=data, headers=headers)
        else:
            return requests.session().post(url, data=data, headers=headers)

    @classmethod
    def put(cls, url, transfer_mode="json", data=None, headers=None):
        """
        执行get请求
        :param url: 请求地址
        :param transfer_mode: 参数传递方式
        :param data: 参数
        :param headers: header值
        :return:
        """
        if transfer_mode == "json":
            return requests.session().put(url, json=data, headers=headers)
        elif transfer_mode == "params":
            return requests.session().post(url, params=data, headers=headers)
        else:
            return requests.session().put(url, data=data, headers=headers)
