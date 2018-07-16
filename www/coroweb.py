# -*- coding:utf-8 -*-


import asyncio
import logging
import os
import functools
import inspect  # 可以获取类或函数的类型，源码，参数信息等的模块
from urllib import parse
from aiohttp import web
from apis import APIError


# ==================================路由修饰器==================================

# 这是个装饰器，在handlers模块中被引用，其作用是给http请求添加请求方法和请求路径这两个属性
# 这是个三层嵌套的decorator（装饰器），目的是可以在decorator本身传入参数
# 这个装饰器将一个函数映射为一个URL处理函数，附带了URL信息
def get(path):
    """
    定义装饰器 @get（"/path")
    这个修饰器作用是给func添加两个属性__method__\__route__,
    方便在add_routes()中判断函数是否可以添加到add_route()路由的依据
    """
    def decorator(func):  # 传入参数是函数
        @functools.wraps(func)
        # 这个函数直接返回原始函数,wrapper.__name__ = func.__name__
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = "GET"  # 给原始函数添加请求方法 “GET”
        wrapper.__route__ = path  # 给原始函数添加请求路径 path
        return wrapper
    return decorator


def post(path):
    """
    定义一个装饰器 @post("/path")
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = "POST"
        wrapper.__route__ = path
        return wrapper
    return decorator


# ==================================请求处理====================================

# 函数的参数fn本身就是个函数，下面五个函数是针对fn函数的参数做一些处理判断
# 这个函数将得到fn函数中的没有默认值的关键词参数的元组
def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY \
                and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


# 这个函数将得到fn函数中的关键词参数的元组
def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


# 判断fn有没有关键词参数，如果有就输出True
def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


# 判断fn有没有可变的关键词参数（**），如果有就输出True
def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


# 判断fn的参数中有没有参数名为request的参数
def has_request_arg(fn):
    # 这里是把之前函数的一句语句拆分为两句，拆分原因是后面要使用中间量sig
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False  # 这个函数默认输出没有参数名为request的参数
    for name, param in params.items():
        if name == "request":
            found = True
            continue
        # request参数必须是最后一个位置和关键词参数
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and
                      param.kind != inspect.Parameter.KEYWORD_ONLY and
                      param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named' +
                             'parameter in function: %s%s'
                             % (fn.__name__, str(sig)))
    return found


# 定义RequestHandler类，封装url处理函数
# RequestHandler的目的是从url函数中分析需要提取的参数,从request中获取必要的参数
# 调用url参数，然后把结果转换为web.Response对象，这样，就完全符合aiohttp框架的要求
class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        # 下面的属性是对传入的fn的参数的一些判断
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    # 定义__call__参数后，其实例可以被视为函数
    @asyncio.coroutine
    def __call__(self, request):
        kw = None  # 假设不存在关键字参数
        # 如果fn的参数有可变的关键字参数或关键字参数
        if self._has_var_kw_arg or self._has_named_kw_args or \
                self._required_kw_args:
            # http method为post的处理
            if request.method == "POST":
                # content_type是request提交的消息主体类型，没有就返回丢失消息主体类型
                if not request.content_type:
                    return web.HTTPBadRequest(body='Missing Content-Type.')
                # 把request.content_type转化为小写
                ct = request.content_type.lower()
                # application/json表示消息主体是序列化后的json字符串
                if ct.startswith("application/json"):
                    params = yield from request.json()  # 用json方法读取信息
                    # 如果读取出来的信息类型不是dict,那json对象一定有问题
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest(body="JSON body must be object.")
                    kw = params  # 把读取出来的dict赋值给kw
                # 以下2种content type都表示消息主体是表单
                elif ct.startswith("application/x-www-form-urlencode") or \
                        ct.startswith("multipart/form-data"):
                    # request.post方法从request body读取POST参数,
                    # 即表单信息,并包装成字典赋给kw变量
                    params = yield from request.post()
                    kw = dict(**params)
                else:  # post的消息主体既不是json对象，又不是浏览器表单，只能报错
                    return web.HTTPBadRequest(
                        body="Unsupported Content-Type: %s" % request,
                        content_type=ct)

            # http method为get的处理
            if request.method == "GET":
                # request.query_string表示url中的查询字符串
                # 比如我百度han，得到网址为https://www.baidu.com/s?ie=UTF-8&wd=han
                # 其中‘ie=UTF-8&wd=han’就是查询字符串
                qs = request.query_string
                if qs:
                    kw = dict()
                    # parse.parse_qs(qs, keep_blank_values=False,
                    # strict_parsing=False)函数的作用是解析一个给定的字符串
                    # keep_blank_values默认为False，指示是否忽略空白值
                    # strict_parsing如果是True，遇到错误是会抛出ValueError错误
                    # 这个函数将返回一个字典
                    # 其中key是等号之前的字符串，value是等号之后的字符串但会是列表
                    # 比如上面的例子就会返回{'ie': ['UTF-8'], 'wd': ['han']}
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]

        # 如果经过以上处理 kw是None，即上面if语句块没有被执行
        # 则获取请求的abstract math info(抽象数学信息),并以字典形式存入kw
        # match_info主要是保存像@get('/blog/{id}')里面的id，就是路由路径里的参数
        if kw is None:
            kw = dict(**request.match_info)
        else:
            # 如果经过以上处理了，kw不为空了，而且没有可变的关键字参数，但是有关键字参数
            if not self._has_var_kw_arg and self._named_kw_args:
                # 下面五行代码的意思是将kw中key为关键字参数的项提取出来保存为新的kw
                # 即剔除kw中key不是fn的关键字参数的项
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # 遍历request.match_info(abstract math info)
            # 再把abstract math info的值加入kw中
            # 若其key即存在于abstract math info又存在于kw中,发出重复参数警告
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning(
                        'Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v

        # 如果fn的参数有'request'，则再给kw中加上request的key和值
        if self._has_request_arg:
            kw['request'] = request

        # 如果fn的参数有，没有默认值的关键字参数
        # 这个if语句块主要是为了检查一下kw
        if self._required_kw_args:
            for name in self._required_kw_args:
                # kw必须包含全部没有默认值的关键字参数，如果发现遗漏则说明有参数没传入，报错
                if name not in kw:
                    return web.HTTPBadRequest(body="Missing argument: %s" % name)
        # 以上过程即为从request中获得必要的参数，并组成kw
        # 以下调用handler处理，并返回response
        logging.info("call with args: %s" % str(kw))
        try:
            r = yield from self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


# ===============================注册路由函数和静态文件路径=========================

# 向app中添加静态文件目录
def add_static(app):
    # os.path.abspath(__file__), 返回当前脚本的绝对路径(包括文件名)
    # os.path.dirname(), 去掉文件名,返回目录路径
    # os.path.join(), 将分离的各部分组合成一个路径名
    # 因此以下操作就是将本文件同目录下的static目录(即www/static/)加入到应用的路由管理器中
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    # app = web.Application(loop = loop)这是在app.py模块中定义的
    app.router.add_static("/static/", path)
    logging.info("add static %s => %s" % ("/static/", path))


# 把请求处理函数注册到app，处理将针对http method和path进行
# 下面的add_routes函数的一部分
def add_route(app, fn):
    method = getattr(fn, "__method__", None)
    path = getattr(fn, "__route__", None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    # 如果函数fn不是一个协程或者生成器，就把这个函数编程协程
    if not asyncio.iscoroutinefunction(fn) and \
            not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info(
        'add route %s %s => %s(%s)' %
        (method, path, fn.__name__, ', '.join(
            inspect.signature(fn).parameters.keys())))
    # 注册request handler
    app.router.add_route(method, path, RequestHandler(app, fn))


# 将handlers模块中所有请求处理函数提取出来交给add_route自动去处理
def add_routes(app, module_name):
    # 如果handlers模块在当前目录下，传入的module_name就是handlers
    # 如果handlers模块在handler目录下没那传入的module_name就是handler.handlers

    # Python rfind() 返回字符串最后一次出现的位置，如果没有匹配项则返回-1。
    n = module_name.rfind('.')
    if n == (-1):
        # import sys <==>sys = __import__('sys')
        mod = __import__(module_name, globals(), locals())
    else:
        # 当module_name为handler.handlers时，[n+1:]就是取.后面的部分，也就是handlers
        name = module_name[n + 1:]
        # 下面的语句相当于执行了两个步骤，传入的module_name是aaa.bbb
        # 第一个步骤相当于from aaa import bbb导入模块以及子模块
        # 第二个步骤通过getattr()方法取得子模块名, 如datetime.datetime
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]),
                      name)
    # dir()不带参数时，返回当前范围内的变量、方法和定义的类型列表；
    # 带参数时，返回参数的属性、方法列表。
    # 如果参数包含方法__dir__()，该方法将被调用。
    # 如果参数不包含__dir__()，该方法将最大限度地收集参数信息。
    for attr in dir(mod):
        # 忽略以_开头的属性与方法,_xx或__xx指示方法或属性为私有的,__xx__指示为特殊变量
        # 私有的,能引用,但不应引用;特殊的,可以直接应用,但一般有特殊用途
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)  # 排除私有属性后，就把属性提取出来
        if callable(fn):  # 查看提取出来的属性是不是函数
            # 如果是函数，再判断是否有__method__和__route__属性
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            # 如果存在则使用app_route函数注册
            if method and path:
                add_route(app, fn)
