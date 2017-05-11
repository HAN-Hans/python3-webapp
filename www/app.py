# !/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'Justin Han'
'''
    由于这个Web App建立在asyncio的基础上，
    使用Jinja2模板引擎渲染前端模板，
    所有数据储存在MySQL，利用aiomysql实现异步驱动
    因此用aiohttp写一个基本的app.py，包含日志、用户和评论
'''

# logging模块是对应用程序或库实现一个灵活的事件日志处理系统
# 日志级别大小关系为：CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
# 用basiconfig()函数设置logging的默认level为INFO
import logging; logging.basicConfig(level=logging.INFO)
# asyncio实现单线程异步IO,一处异步，处处异步
# os提供调用操作系统的接口函数
# json提供python对象到Json的转换
# time为各种时间操作函数，datatime处理日期时间标准库
import asyncio, os, json, time
from datetime import datetime
# aiohttp是基于asyncio的http框架
from aiohttp import web
# Jinja2 是仿照 Django 模板的 Python 前端引擎模板
# Environment指的是jinjia2模板的配置环境
# FileSystemLoader是文件系统加载器，用来加载模板路径
from jinja2 import Environment, FileSystemLoader
import orm
from coroweb import add_routes, add_static
import handlers

# 这个函数的功能是初始化jinja2模板，配置jinja2的环境
def init_jinja2(app,**kw):
    logging.info('init jinja2...')
    # 设置解析模板需要用到的环境变量
    options = dict(
        autoescape = kw.get('autoescape', True),  # 自动转义xml/html的特殊字符
        # 下面两句的意思是{%和%}中间的是python代码而不是html
        block_start_string = kw.get('block_start_string', '{%'),        # 设置代码起始字符串
        block_end_string = kw.get('block_end_string', '%}'),            # 设置代码的终止字符串
        variable_start_string = kw.get('variable_start_string', '{{'),  # 这两句分别设置了变量的起始和结束字符串
        variable_end_string = kw.get('variable_end_string', '}}'),      # 就是说{{和}}中间是变量，看过templates目录下的test.html文件后就很好理解了
        auto_reload = kw.get('auto_reload', True)                       # 当模板文件被修改后，下次请求加载该模板文件的时候会自动加载修改后的模板文件
    )
    path = kw.get('path', None)  # 从kw中获取模板路径，如果没有传入这个参数则默认为None
    # 如果path为None，则将当前文件所在目录下的templates目录设为模板文件目录
    if path is None:
        # os.path.abspath(__file__)取当前文件的绝对目录
        # os.path.dirname()取绝对目录的路径部分
        # os.path.join(path， name)把目录和名字组合
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    # loader=FileSystemLoader(path)指的是到哪个目录下加载模板文件， **options就是前面的options
    env = Environment(loader = FileSystemLoader(path), **options)
    filters = kw.get('filters', None)  # fillters=>过滤器
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f  # 在env中添加过滤器
    # 前面已经把jinjia2的环境配置都赋值给env了，这里再把env存入app的dict中，这样app就知道要去哪找模板，怎么解析模板
    app['__templating__'] = env

# 这个函数的作用就是当http请求的时候，通过logging.info输出请求的信息，其中包括请求的方法和路径
@asyncio.coroutine
def logger_factory(app, handler):
    @asyncio.coroutine
    def logger(request):
        # 记录日志
        logging.info('Request: %s %s' % (request.method, request.path))
        # 继续处理请求
        return (yield from handler(request))
    return logger

# 只有当请求方法为POST时这个函数才起作用
@asyncio.coroutine
def data_factory(app, handler):
    @asyncio.coroutine
    def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = yield from request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = yield from request.post()
                logging.info('request form: %s' % str(request.__data__))
        return (yield from handler(request))
    return parse_data

# response这个middleware把返回值转换为web.Response对象再返回，以保证满足aiohttp的要求：
@asyncio.coroutine
def response_factory(app, handler):
    @asyncio.coroutine
    def response(request):
        logging.info('Response handler...')
        r = yield from handler(request)
        # 如果相应结果为StreamResponse，直接返回treamResponse是aiohttp定义response的基类,
        # 即所有响应类型都继承自该类StreamResponse主要为流式数据而设计
        if isinstance(r, web.StreamResponse):
            return r
        # 如果相应结果为字节流，则将其作为应答的body部分，并设置响应类型为流型
        if isinstance(r, bytes):
            resp = web.Response(body = r)
            resp.content_type = 'application/octet-stream'
            return resp
        # 如果响应结果为字符串
        if isinstance(r, str):
            # 判断响应结果是否为重定向，如果是，返回重定向后的结果
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])  # 即把r字符串之前的"redirect:"去掉
            # 然后以utf8对其编码，并设置响应类型为html型
            resp = web.Response(body = r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        # 如果响应结果是字典，则获取他的jinja2模板信息，此处为jinja2.env
        if isinstance(r, dict):
            template = r.get('__template__')
            # 若不存在对应模板，则将字典调整为json格式返回，并设置响应类型为json
            if template is None:
                resp = web.Response(body = json.dumps(r, ensure_ascii = False, default = lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body = app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        # 如果响应结果为整数型，且在100和600之间
        # 则此时r为状态码，即404，500等
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        # 如果响应结果为长度为2的元组
        # 元组第一个值为整数型且在100和600之间
        # 则t为http状态码，m为错误描述，返回状态码和错误描述
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
        # 默认以字符串形式返回响应结果，设置类型为普通文本
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
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
@asyncio.coroutine
def init(loop):
    # 创建数据库连接池
    yield from orm.create_pool(loop = loop, host = '127.0.0.1', port = 3306, \
        user = 'root', password = '12125772', db = 'awesome')
    # middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理。
    # 一个middleware可以改变URL的输入、输出，甚至可以决定不继续处理而直接返回。
    # middleware的用处就在于把通用的功能从每个URL处理函数中拿出来，集中放到一个地方。
    app = web.Application(loop = loop, middlewares = [logger_factory, response_factory])
    # 初始化jinja2模板，并传入时间过滤器
    init_jinja2(app, filters = dict(datetime = datetime_filter))
    # 下面这两个函数在coroweb模块中
    add_routes(app, 'handlers')     # handlers指的是handlers模块也就是handlers.py
    add_static(app)                 # 加静态文件目录
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv



# asyncio的编程模块实际上就是一个消息循环。我们从asyncio模块中直接获取一个eventloop（事件循环）的引用，
# 然后把需要执行的协程扔到eventloop中执行，就实现了异步IO

# 第一步是获取eventloop
# get_event_loop() => 获取当前脚本下的事件循环，返回一个event loop对象(这个对象的类型是
# 'asyncio.windows_events._WindowsSelectorEventLoop')，实现AbstractEventLoop（事件循环的基类）接口
# 如果当前脚本下没有事件循环，将抛出异常，get_event_loop()永远不会抛出None
loop = asyncio.get_event_loop()
# 之后是执行curoutine
loop.run_until_complete(init(loop))
# 无限循环运行直到stop()
loop.run_forever()



