#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''
# 通常，一个Web App在运行时都需要读取配置文件，比如数据库的用户名、口令等
# 在不同的环境中运行时，Web App可以通过读取不同的配置文件来获得正确的配置
__author__ = 'Justin HAN'

# 默认的配置文件config_default.py应该完全符合本地开发环境，
# 这样，无需任何设置，就可以立刻启动服务器
configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '12125772',
        'db': 'awesome'
    },
    'session': {
        'secret': 'Awesome'
    }
}
