###!/usr/bin/env python3
### -*- coding: utf-8 -*-
##
##__author__ = 'Justin Han'
##
##' url handlers '
##
##from coroweb import get, post
##from aiohttp import web
##
##@get('/blog')
##async def handler_url_blog(request):
##    body='<h1>Awesome: /blog</h1>'
##    return body
##
##@get('/greeting')
##async def handler_url_greeting(*,name,request):
##    body='<h1>Awesome: /greeting %s</h1>'%name
##    return body
##
##@get('/input')
##async def handler_url_input(request):
##    body='<form action="/result" method="post">E-mail: <input type="email" name="user_email" /><input type="submit" /></form>'
##    return body
##
##@post('/result')
##async def handler_url_result(*,user_email,request):
##    body='<h1>您输入的邮箱是%s</h1>'%user_email
##    return body
##
##@get('/index')
##async def handler_url_index(request):
##    body='<h1>Awesome: /index</h1>'
##    return body
##
##@get('/create_comment')
##async def handler_url_create_comment(request):
##    body='<h1>Awesome: /create_comment</h1>'
##    return body


##===================================================================


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from coroweb import get, post
from aiohttp import web

__author__ = 'Michael Liao'

' url handlers '

@get('/blog')
async def handler_url_blog(request):
    return web.Response(body=b'<h1>Awesome: /blog</h1>', content_type='text/html', charset='UTF-8')

@get('/index')
async def handler_url_index(request):
    return web.Response(body=b'<h1>Awesome: /index</h1>', content_type='text/html', charset='UTF-8')

@get('/create_comment')
async def handler_url_create_comment(request):
    return web.Response(body=b'<h1>Awesome>: /create_comment</h1', content_type='text/html', charset='UTF-8')
