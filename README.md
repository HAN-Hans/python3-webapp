# python3-webapp
 
Asesome Pyhthon3 WebApp 项目回顾与总结

***

## #引言

这个项目是大概花了一个多月时间完成的，代码几乎全是参考[实战](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432170876125c96f6cc10717484baea0c6da9bee2be4000) 自己一个一个敲出来的。期间我查阅了许多[资料](#reference), 几乎为每一行代码自己都加了比较详细的注释。这样能够在自己理解python-webapp源代码的同时，加深对python基础语法的理解。暂时这个个人博客还没有部署在服务器上，我打算在学习完前端知识后将前端页面修改好后再部署到服务器上。

> 注：本项目源代码与[Python3教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)代码基本一样，主要是在代码中间注释中添加自己对代码的理解

## #正文

***开发环境***

* python版本：python3.6.1		
* 异步框架：[asyncio](https://docs.python.org/3/library/asyncio.html)
	* [aiohttp](http://aiohttp.readthedocs.org/en/stable/web.html)
	* [aiomysql](http://aiomysql.readthedocs.io/en/latest/index.html)
* 前端模板引擎：[jinja2](http://jinja.pocoo.org/docs/latest/)
* 数据库：MySQL5.6

***项目结构***

    python3-webapp     <-- 根目录
	  ├─backup           <-- 备份目录			
	  ├─conf             <-- 配置文件
	  │  ├─nginx
	  │  └─supervisor
	  ├─ios              <-- 存放iOS App工程
	  │  └─AwesomeApp.xcodeproj
	  │      └─project.xcworkspace
	  └─www              <-- Web目录
	      ├─static       <-- 存放静态文件
	      │  ├─css
	      │  │  └─addons
	      │  ├─fonts
	      │  ├─img
	      │  └─js
	      ├─templates    <-- 存放模板文件
	      └─__pycache__

其中我们的代码主要是放在/www/文件夹中

	www				<-- Web目录
	│  apis.py			<-- api异常和分页定义
	│  app.py			<-- Webapp主程序
	│  config.py			<-- 配置文件
	│  config_default.py		<-- 默认的配置文件
	│  config_override.py		<-- 动态的配置文件
	│  coroweb.py			<-- webapp框架
	│  handlers.py			<-- url请求处理
	│  markdown2.py			<-- text-to-HTML执行markdown的python模块
	│  models.py			<-- 对象模型，USer、Blog、Comment 三个对象
	│  orm.py			<-- 对象模型表示的对象映射到基于SQL的关系模型数据库结构中去
	│  pymonitor.py			<-- 对文件监控如果有修改不需要重启进程
	│  schema.sql			<-- 简单的sql脚本，用于创建database表，项目ORM中就可以实现
	│  test.py			<-- 项目过程中的测试文件

## #

## 部分学习材料

<p id="reference"></p>

***[stackoverflow python](http://stackoverflow.com/questions/tagged/python?page=2&sort=votes&pagesize=15)***

- [What is a metaclass in Python?](http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python)
- [What is the difference between @staticmethod and @classmethod in Python?](http://stackoverflow.com/questions/136097/what-is-the-difference-between-staticmethod-and-classmethod-in-python)
- [What does the “yield” keyword do in Python?](http://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python)
- [In practice, what are the main uses for the new “yield from” syntax in Python 3.3?](http://stackoverflow.com/questions/9708902/in-practice-what-are-the-main-uses-for-the-new-yield-from-syntax-in-python-3)


参考：[Python3教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)

