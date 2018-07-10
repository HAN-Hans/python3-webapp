""" async web application

这个 Web App 建立在 asyncio 的基础上，
使用 Jinja2 模板引擎渲染前端模板，
所有数据储存在 MySQL ，利用 aiomysql 实现异步驱动
"""


__version__ = '0.2'
__author__ = 'hhwe'

import os
import json
import time
import logging
import asyncio
from aiohttp import web
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

import orm
import config
from coroweb import add_routes, add_static
from handlers import cookie2user, COOKIE_NAME


# logging初始化设置
logging.basicConfig(
    level=logging.INFO,filename='/tmp/test.log',
    filemode='w',
    format="%(asctime)s %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
)


# 这个函数的功能是初始化jinja2模板，配置jinja2的环境
def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    # 设置解析模板需要用到的环境变量
    options = dict(
        autoescape=kw.get('autoescape', True),  # 自动转义xml/html的特殊字符
        # 下面两句的意思是{%和%}、{{和}}中间的是python代码而不是html
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)  # 从kw中获取模板路径，如果没有传入这个参数则默认为None
    # 如果path为None，则将当前文件所在目录下的templates目录设为模板文件目录
    if path is None:
        # os.path.abspath(__file__)取当前文件的绝对目录
        # os.path.dirname()取绝对目录的路径部分
        # os.path.join(path， name)把目录和名字组合
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'templates')
    logging.info('set jinja2 template path: %s' % path)
    # loader=FileSystemLoader(path)指的是到哪个目录下加载模板文件，
    # **options就是前面的options
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)  # fillters=>过滤器
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f  # 在env中添加过滤器
    # 前面已经把jinjia2的环境配置都赋值给env了
    # 这里再把env存入app的dict中，这样app就知道要去哪找模板，怎么解析模板
    app['__templating__'] = env


# 当http请求的时候，通过logging.info输出请求的信息，其中包括请求的方法和路径
async def logger_factory(app, handler):
    async def logger(request):
        # 记录日志
        logging.info('Request: %s %s' % (request.method, request.path))
        # 继续处理请求
        return await handler(request)
    return logger


# 在处理请求之前,先将cookie解析出来,并将登录用于绑定到request对象上
# 这样后续的url处理函数就可以直接拿到登录用户
# 以后的每个请求,都是在这个middle之后处理的,都已经绑定了用户信息
async def auth_factory(app, handler):
    async def auth(request):
        logging.info("check user: %s %s" % (request.method, request.path))
        request.__user__ = None  # 先绑定一个None到请求的__user__属性
        # 通过cookie名取得加密cookie字符串
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)  # 验证cookie,并得到用户信息
            if user:
                logging.info("set current user: %s" % user.email)
                request.__user__ = user  # 将用户信息绑定到请求上
        # 请求的路径是管理页面,但用户非管理员,将会重定向到登录页面?
        if request.path.startswith('/manage/') and \
                (request.__user__ is None or not request.__user__.admin):
            return web.HTTPFound('/signin')
        return await handler(request)
    return auth


# 解析数据
async def data_factory(app, handler):
    async def parse_data(request):
        # 解析数据是针对post方法传来的数据不是post,将跳过,直接调用handler处理请求
        if request.method == "POST":
            # content_type字段表示post的消息主体的类型
            # request.json方法,读取消息主题,并以utf-8解码
            # 将消息主体存入请求的__data__属性
            if request.content_type.startswith("application/json"):
                request.__data__ = await request.json()
                logging.info("request json: %s" % str(request.__data__))
            # content type字段application/x-www-form-urlencodeed是浏览器表单
            # request.post方法读取post来的消息主体,即表单信息
            elif request.content_type.startswith(
                    "application/x-www-form-urlencoded"):
                request.__data__ = await request.post()
                logging.info("request form: %s" % str(request.__data__))
        # 调用传入的handler继续处理请求
        return await handler(request)
    return parse_data


# 上面factory是在url处理函数之前先对请求进行了处理,以下则在url处理函数之后进行处理
# 其将request handler的返回值转换为web.Response对象
async def response_factory(app, handler):
    async def response(request):
        logging.info("Response handler...")
        # 调用handler来处理url请求,并返回响应结果
        r = await handler(request)
        # 若响应结果为StreamResponse,直接返回
        # StreamResponse是aiohttp定义response的基类,即所有响应类型都继承自该类
        # StreamResponse主要为流式数据而设计
        if isinstance(r, web.StreamResponse):
            return r
        # 若响应结果为字节流,则将其作为应答的body部分,并设置响应类型为流型
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = "application/octet-stream"
            return resp
        # 若响应结果为字符串
        if isinstance(r, str):
            # 判断响应结果是否为重定向.若是,则返回重定向的地址
            if r.startswith("redirect:"):
                return web.HTTPFound(r[9:])
            # 响应结果不是重定向,则以utf-8对字符串进行编码,作为body.设置相应的响应类型
            resp = web.Response(body=r.encode("utf-8"))
            resp.content_type = "text/html;charset=utf-8"
            return resp
        # 若响应结果为字典,则获取它的模板属性,此处为jinja2.env(见init_jinja2)
        if isinstance(r, dict):
            template = r.get("__template__")
            # 若不存在对应模板,则将字典调整为json格式返回,并设置响应类型为json
            if template is None:
                resp = web.Response(
                    body=json.dumps(
                        r,
                        ensure_ascii=False,
                        default=lambda o: o.__dict__).encode("utf-8"))
                resp.content_type = "application/json;charset=utf-8"
                return resp
            # 存在对应模板的,则将套用模板,用request handler的结果进行渲染
            else:
                # 增加__user__,前端页面将依次来决定是否显示评论框
                r["__user__"] = request.__user__
                resp = web.Response(
                    body=app["__templating__"]. get_template(template).render(
                        **r).encode("utf-8"))
                resp.content_type = "text/html;charset=utf-8"
                return resp
        # 若响应结果为整型的
        # 此时r为状态码,即404,500等
        if isinstance(r, int) and 100 <= r < 600:
            return web.Response
        # 若响应结果为元组,并且长度为2
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            # t为http状态码,m为错误描述
            # 判断t是否满足100~600的条件
            if isinstance(t, int) and 100 <= t < 600:
                # 返回状态码与错误描述
                return web.Response(t, str(m))
        # 默认以字符串形式返回响应结果,设置类型为普通文本
        resp = web.Response(body=str(r).encode("utf-8"))
        resp.content_type = "text/plain;charset=utf-8"
        return resp
    return response


# 时间过滤器，作用是返回日志创建的时间，用于显示在日志标题下面
def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


# 调用asyncio实现异步IO
async def init(loop):
    # 创建数据库连接池
    await orm.create_pool(loop=loop, **config.db)
    # 创建web应用对象, 并传入中间件
    app = web.Application(loop=loop, middlewares=[
        logger_factory, auth_factory, response_factory])
    # 初始化jinja2模板，并传入时间过滤器
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    # 下面这两个函数在coroweb模块中
    add_routes(app, 'handlers')  # handlers指的是handlers模块也就是handlers.py
    add_static(app)  # 加静态文件目录
    # loop.create_server()则利用asyncio创建TCP服务
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    logging.info('server started at http://127.0.0.1:8000...')
    return srv


if __name__ == "__main__":
    # 获取EventLoop:
    loop = asyncio.get_event_loop()
    # 之后是执行curoutine
    loop.run_until_complete(init(loop))
    # 无限循环运行直到stop()
    loop.run_forever()
