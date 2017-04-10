#!/usr/bin/python
#-*- coding:utf-8 -*-

__author__ = 'Justin Han'
'''
    由于这个Web App建立在asyncio的基础上，因此用aiohttp写一个基本的app.py
'''

#logging模块是对应用程序或库实现一个灵活的事件日志处理系统，日志级别大小关系为：CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET，用basiconfig()函数设置logging的默认level为INFO
import logging; logging.basicConfig(level=logging.INFO)

#asyncio实现单线程异步IO
#os提供调用操作系统的接口函数
#json提供python对象到Json的转换
#time为各种时间操作函数，datatime处理日期时间标准库
import asyncio, os, json, time
from datetime import datetime

#aiohttp是基于asyncio的http框架
from aiohttp import web

#定义http访问请求方法,主页index
def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',content_type='text/html')

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

#get_event_loop获取当前脚本的消息环，返还一个event loop对象
loop = asyncio.get_event_loop()
#执行curoution
loop.run_until_complete(init(loop))
#无限循环运行知道stop()
loop.run_forever()


