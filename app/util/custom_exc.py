#!python3.7
# -*- coding:utf-8 -*-

# @ProjectName = 'fastapi'
# @Author = 'xujianbo'
# @Time = '2020/11/12 16:18'
"""

自定义异常

"""


class UserTokenError(Exception):
    def __init__(self, err_desc: str = "用户认证异常"):
        self.err_desc = err_desc


class UserNotFound(Exception):
    def __init__(self, err_desc: str = "没有此用户"):
        self.err_desc = err_desc


class PostParamsError(Exception):
    def __init__(self, err_desc: str = "POST请求参数错误"):
        self.err_desc = err_desc


class UserPasswordError(Exception):
    def __init__(self, err_desc: str = "登录密码错误"):
        self.err_desc = err_desc


class UserRoleError(Exception):
    def __init__(self, err_desc: str = "登录角色不正确"):
        self.err_desc = err_desc


class PermissError(Exception):
    def __init__(self, err_desc: str = "没有此权限"):
        self.err_desc = err_desc
