import traceback

import redis
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api.api_login import loginApp
from app.api.project import projectApp
from app.api.report import reportApp
from app.api.setting import settingApp
from app.api.user import userApp
from .config import BACKEND_CORS_ORIGINS, PROJECT_NAME, DESCRIPTION, STATIC_PATH, PROJECT_DIR
from .util import response_code, logger
from .util.custom_exc import *


def create_app():
    """
    生成FastAPI对象
    :return:
    """
    app = FastAPI(title=PROJECT_NAME, version="1.0", description=DESCRIPTION)
    # 挂载静态文件
    app.mount(path="/app/", app=StaticFiles(directory=STATIC_PATH), name="static")
    app.mount(path="/app/", app=StaticFiles(directory=PROJECT_DIR), name="reports")
    app.include_router(loginApp, prefix='/api', tags=['用户'])
    app.include_router(userApp, prefix='/api', tags=['用户'])
    app.include_router(projectApp, prefix='/api', tags=['项目'])
    app.include_router(reportApp, prefix='/api', tags=['报告'])
    app.include_router(settingApp, prefix='/api', tags=['配置'])
    # 跨域设置
    register_cors(app)
    # 注册全局异常
    register_exception(app)
    # 注册全局Redis
    register_redis(app)
    return app


def register_redis(app: FastAPI) -> None:
    """
        把redis挂载到app对象上面
        :param app:
        :return:
    """

    @app.on_event('startup')
    def startup_event():
        """
            获取链接
            :return:
        """
        app.state.redis = redis.StrictRedis(host=config.REDIS_SERVER, port=config.REDIS_PORT, db=config.REDIS_DB,
                                            encoding='utf-8',
                                            socket_timeout=3,
                                            retry_on_timeout=3)

    @app.on_event('shutdown')
    async def shutdown_event():
        """
            关闭
            :return:
        """
        app.state.redis.close()


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


def register_exception(app: FastAPI):
    """
    全局异常捕获

    注意 别手误多敲一个s

    exception_handler
    exception_handlers
    两者有区别

        如果只捕获一个异常 启动会报错
        @app.exception_handlers(UserNotFound)
    TypeError: 'dict' object is not callable

    :param app:
    :return:
    """

    # 自定义异常 捕获
    @app.exception_handler(UserNotFound)
    async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
        """
        用户认证未找到
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"token未知用户\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")

        return response_code.resp_5001(message=exc.err_desc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        token信息为空
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"{exc.detail}\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        if exc.detail == "Not authenticated":
            return response_code.resp_5001(message="用户认证异常!")
        return response_code.resp_401(message=exc.detail)

    @app.exception_handler(IntegrityError)
    async def inte_exception_handler(request: Request, exc: IntegrityError):
        """
        数据重复
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"{exc.detail}\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return response_code.resp_401(message='数据已存在！')

    @app.exception_handler(UserTokenError)
    async def token_error_exception_handler(request: Request, exc: UserTokenError):
        """
        用户token异常
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"用户认证异常\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")

        return response_code.resp_5001(message=exc.err_desc)

    @app.exception_handler(PermissError)
    async def permiss_exception_handler(request: Request, exc: PermissError):
        """
        没有该权限
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"没有此权限\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")

        return response_code.resp_5000(message=exc.err_desc)

    @app.exception_handler(UserPasswordError)
    async def password_exception_handler(request: Request, exc: UserPasswordError):
        """
        用户密码错误
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"登录密码错误\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")

        return response_code.resp_5001(message=exc.err_desc)

    @app.exception_handler(PostParamsError)
    async def query_params_exception_handler(request: Request, exc: PostParamsError):
        """
        内部查询操作时，其他参数异常
        :param request:
        :param exc:
        :return:
        """
        # logger.error(f"参数查询异常\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")

        return response_code.resp_401(message=exc.err_desc)

    @app.exception_handler(ValidationError)
    async def inner_validation_exception_handler(request: Request, exc: ValidationError):
        """
        内部参数验证异常
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"内部参数参数错误\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return response_code.resp_500(message=exc.errors())

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        请求参数验证异常
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"参数错误\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return response_code.resp_422(message=exc.errors())

    # 捕获全部异常
    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        全局所有异常
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"全局异常\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return response_code.resp_500(message="服务器内部错误")
