# 数据库配置
# MYSQL数据库配置
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import AnyHttpUrl
import sys
import os

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
ROOT_PATH = os.path.split(CUR_PATH)[0]
sys.path.append(ROOT_PATH)
STATIC_PATH = CUR_PATH + "/static"
PROJECT_DIR = os.path.split(ROOT_PATH)[0] + "/projects"
REPORT_DIR = os.path.split(ROOT_PATH)[0] + "/reports"

# MYSQL_SERVER: str = 'vertex-dev-rds-aurora-cluster-cluster.cluster-chhckevzza3k.ap-southeast-1.rds.amazonaws.com'
MYSQL_SERVER:str = "127.0.0.1"
MYSQL_USER: str = 'decodedev'
MYSQL_PASSWORD: str = 'qQ57FT1kttGZ6dMmuyNeh9XN'
MYSQL_PORT: str = '3306'
MYSQL_DB: str = 'user'
SQLALCHEMY_DATABASE_URI: str = rf'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8'

ADMIN_FX: str = "https://vertex-api.dev.decodebackoffice.com"

# REDIS数据库配置
REDIS_SERVER: str = '172.29.10.204'
REDIS_PORT: str = '6380'
REDIS_DB: str = '0'

# 是否开启日志
DEBUG = False

# 认证相关配置
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

PROJECT_NAME = "LOCUST性能测试平台API"
DESCRIPTION = "LOCUST性能测试平台API文档"

# 支持跨域
BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['*']
# 上传的文件格式
ALLOWED_EXTENSIONS = {"rar", "zip", "gz", "tgz", "xz", "bz2"}
