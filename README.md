# python3-webapp
 
Asesome Pyhthon3 WebApp 项目回顾与总结

***

## #引言

这个项目是大概花了一个多月时间完成的，代码几乎全是参考[实战](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432170876125c96f6cc10717484baea0c6da9bee2be4000) 自己一个一个敲出来的。期间我查阅了许多[资料](#reference), 几乎为每一行代码自己都加了比较详细的注释。这样能够在自己理解python-webapp源代码的同时，加深对python基础语法的理解。暂时这个个人博客还没有部署在服务器上，我打算在学习完前端知识后将前端页面修改好后再部署到服务器上。

> 注：本项目源代码与[Python3教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)代码基本一样，主要是在代码中间注释中添加自己对代码的理解

***

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

	www			<-- Web目录
	│  apis.py		<-- 定义了APIError类和Page类，分别处理api异常和分页管理
	│  app.py		<-- Webapp主程序，初始化了`jinja2`环境, 实现了各`middleware factory`, 创建了app对象, 完成系统初始化
	│  config.py		<-- 配置文件，把config_default.py作为开发环境的标准配置，把config_override.py作为生产环境的标准配置
	│  config_default.py	<-- 默认的配置文件
	│  config_override.py	<-- 动态的配置文件
	│  coroweb.py		<-- webapp框架，说白了就是事务处理(`handler`)的基础准备
	│  handlers.py		<-- url请求处理，用于向前端提供和收集数据
	│  markdown2.py		<-- text-to-HTML执行markdown的python模块库文件
	│  models.py		<-- 在ORM基础上建立集体的类，USer、Blog、Comment 三个对象
	│  orm.py		<-- 建立ORM, 此处所有代码都是为此服务的——创建了全局数据库连接池, 封装sql操作, 自定义元类, 定义Model类
	│  pymonitor.py		<-- 对文件监控如果有修改不需要重启进程
	│  schema.sql		<-- 简单的sql脚本，用于创建database表，项目ORM中就可以实现
	│  test.py		<-- 项目过程中的测试文件

## #程序流程

在项目中我们使用logging模块打印程序运行信息，通过logging我们可以方便的了解程序大致流程
开始运行webapp我们可以在控制台上看到如下信息：

```
1、======================================================================================
D:\python3-webapp\www>python pymonitor.py app.py
[Monitor] Watch directory D:\python3-webapp\www...	
[Monitor] Start process python app.py...
2、=======================================================================================
found Model:User (table:users
found mapping：id ==> <StringField, varchar(50):None>
found mapping：email ==> <StringField, varchar(50):None>
found mapping：passwd ==> <StringField, varchar(50):None>
found mapping：admin ==> <BooleanField, boolean:None>
found mapping：name ==> <StringField, varchar(50):None>
found mapping：image ==> <StringField, varchar(500):None>
found mapping：created_at ==> <FloatField, real:None>
found Model:Blog (table:blogs
found mapping：id ==> <StringField, varchar(100):None>
found mapping：user_id ==> <StringField, varchar(50):None>
found mapping：user_name ==> <StringField, varchar(50):None>
found mapping：user_image ==> <StringField, varchar(500):None>
found mapping：name ==> <StringField, varchar(50):None>
found mapping：summary ==> <StringField, varchar(200):None>
found mapping：content ==> <TextField, text:None>
found mapping：created_at ==> <FloatField, real:None>
Comment (table:comments
found mapping：id ==> <StringField, varchar(100):None>
found mapping：blog_id ==> <StringField, varchar(50):None>
found mapping：user_id ==> <StringField, varchar(50):None>
found mapping：user_name ==> <StringField, varchar(50):None>
found mapping：user_image ==> <StringField, varchar(500:None>
found mapping：content ==> <TextField, text:None>
found mapping：created_at ==> <FloatField, real:None>
create a database connection pool...
3、========================================================================================
init jinja2...
set jinja2 template path: D:\python3-webapp\www\templates
4、========================================================================================
add route GET /api/blogs => api_blogs(page)
add route GET /api/comments => api_comments(page)
add route POST /api/blogs => api_create_blog(request, name, summary, content)
add route POST /api/blogs/{id}/comments => api_create_comment(id, request, content)
add route POST /api/blogs/{id}/delete => api_delete_blog(request, id)
add route POST /api/comments/{id}/delete => api_delete_comment(id, request)
add route GET /api/blogs/{id} => api_get_blog(id)
add route GET /api/users => api_get_users(page)
add route POST /api/users => api_register_user(name, email, passwd)
add route POST /api/blogs/{id} => api_update_blog(id, request, name, summary, content)
add route POST /api/authenticate => authenticate(email, passwd)
add route GET /blog/{id} => get_blog(id)
add route GET / => index(page)
add route GET /manage/ => manage()
add route GET /manage/blogs => manage_blogs(page)
add route GET /manage/comments => manage_comments(page)
add route GET /manage/blogs/create => manage_create_blog()
add route GET /manage/blogs/edit => manage_edit_blog(id)
add route GET /manage/users => manage_users(page)
add route GET /register => register()
add route GET /signin => signin()
add route GET /signout => signout(request)
5、========================================================================================
add static /static/ => D:\python3-webapp\www\static
6、========================================================================================
server started at http://127.0.0.1:9000...
```
由日志可知, 服务器启动之后进行了以下初始化操作:

1. [Monitor]日志是用来记录文件修改情况的，通过系统API监控相关文件是否改动，若有文件修改就会自动重启进程，能够有效避免修改代码后重复手动执行

```
[Monitor] python source file changed: D:\python3-webapp\www\pymonitor.py
[Monitor] Kill process [10184]...
[Monitor] Process ended with code 1
[Monitor] Start process python app.py...
[Monitor] python source file changed: D:\python3-webapp\www\pymonitor.py
[Monitor] Kill process [6356]...
[Monitor] Process ended with code 1
[Monitor] Start process python app.py...
```
2. **建立model**, 简单点说就是建立python中的`类`与数据库中的`表`的映射关系
3. **创建全局数据库连接池**, 按廖老师的说法, 这是为了使每个http请求都可以从连接池中直接获取数据库连接, 而不必频繁地打开关闭数据库连接. 现在你真的意识到`orm.py`的重要性了吗? 很重要, 与数据打交道的活在其中都做了定义
3. **初始化`jinja2`引擎, 并设置模板的路径**, 主要是初始化了`jinja2 env`(环境), 并将`jinja2 env`绑定到`webapp`的`__templating__`属性上. 这是因为在初始化`jinja2 env`时, 指定了加载器(`loader`)为文件系统加载器(`FileSystemLoader`).
4. **注册处理器(handler)** `事务处理`的三要素: `方法(http method)` &  `路径(path)` & `处理函数(func)`. 将三者连起来看就是, 将对某路径的某种http请求交给某个函数处理, 而该函数就称为某路径上某种请求的处理器(handler).
5. **加载静态资源**
6. **创建服务器对象, 并绑定到socket**

当客户端随机提交一个请求时webapp又抛出一些响应的信息
```
1、============================================================================================
Request: GET /
check user: GET /
Response handler...
2、===========================================================================================
call with args: {}
3、===========================================================================================
SQL sentence：select count(id) _num_ from `blogs`
rows returned：1
SQL sentence：select `id`, `user_id`,`user_name`,`user_image`,`name`,`summary`,`content`,`created_at` from `blogs` limit ?,?
rows returned：1
```


仔细看, 你会发现, 从上到下的过程就是一个实现`MVC`模型的过程: `建立model` -> `构建前端视图` -> `注册处理控制`. 



## #


## 参考资料

<p id="reference"></p>

***[stackoverflow python](http://stackoverflow.com/questions/tagged/python?page=2&sort=votes&pagesize=15)***

- [What is a metaclass in Python?](http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python)
- [What is the difference between @staticmethod and @classmethod in Python?](http://stackoverflow.com/questions/136097/what-is-the-difference-between-staticmethod-and-classmethod-in-python)
- [What does the “yield” keyword do in Python?](http://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python)
- [In practice, what are the main uses for the new “yield from” syntax in Python 3.3?](http://stackoverflow.com/questions/9708902/in-practice-what-are-the-main-uses-for-the-new-yield-from-syntax-in-python-3)

【参考教程】：
【[Python3教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)】
【[python官方手册](https://docs.python.org/3/tutorial/index.html)】
