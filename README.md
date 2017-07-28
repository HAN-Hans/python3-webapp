# python3-webapp

Asesome Pyhthon3 WebApp 项目回顾与总结

***

# #引言

这个项目是大概花了一个多月时间完成的，代码几乎全是参考[实战](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432170876125c96f6cc10717484baea0c6da9bee2be4000) 自己一个一个敲出来的。期间我查阅了许多[资料](#reference), 对于不理解的自己都加了比较详细的注释。这样能够在自己理解python-webapp源代码的同时，加深对python基础语法的理解。

> 注：本项目源代码与[Python3教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)代码基本一样，主要是在代码中间注释中添加自己对代码的理解

***

# #正文

## 开发环境

* python版本：python3.6.1		
* 异步框架：[asyncio](https://docs.python.org/3/library/asyncio.html)
	* [aiohttp](http://aiohttp.readthedocs.org/en/stable/web.html)
	* [aiomysql](http://aiomysql.readthedocs.io/en/latest/index.html)
* 前端模板引擎：[jinja2](http://jinja.pocoo.org/docs/latest/)
* 数据库：MySQL5.6

我使用python3自带的virtual enviroment工具venv搭建一个独立的开发环境：

    $ python3 -m venv env //在根目录中多啦env文件夹，存放所有第三方库

所有的python第三方库文件在requiremen.txt文件中，安装只需在终端运行：

    $ pip3 install -r requiremen.txt

## 项目结构

    python3-webapp     <-- 根目录
	  ├─backup           <-- 备份目录
	  ├─conf             <-- 部署配置文件
	  │  ├─nginx		<-- 高性能Web服务器+负责反向代理
	  │  └─supervisor	<-- 监控服务进程
	  ├─dist			 <-- 项目打包tar
	  ├─fabfile.py		<-- fabric自动化部署
	  ├─ios              <-- 存放iOS App工程
	  │  └─AwesomeApp.xcodeproj
	  │      └─project.xcworkspace
	  ├─requirement.txt		<-- 项目第三方库
	  └─www              <-- Web目录
	      ├─static       <-- 存放静态文件
	      └─templates    <-- 存放模板文件

其中我们的代码主要是放在/www/文件夹中：

	www			<-- Web目录
	├─ apis.py		<-- 定义了APIError类和Page类，分别处理api异常和分页管理
	├─ app.py		<-- Webapp主程序，初始化了`jinja2`环境, 实现了各`middleware factory`, 创建了app对象, 完成系统初始化
	├─ config.py		<-- 配置文件，把config_default.py作为开发环境的标准配置，把config_override.py作为生产环境的标准配置
	├─ config_default.py	<-- 默认的配置文件
	├─ config_override.py	<-- 动态的配置文件
	├─ coroweb.py		<-- webapp框架，说白了就是事务处理(`handler`)的基础准备
	├─ handlers.py		<-- url请求处理，用于向前端提供和收集数据
	├─ markdown2.py		<-- text-to-HTML执行markdown的python模块库文件
	├─ models.py		<-- 在ORM基础上建立集体的类，USer、Blog、Comment 三个对象
	├─ orm.py		<-- 建立ORM, 此处所有代码都是为此服务的——创建了全局数据库连接池, 封装sql操作, 自定义元类, 定义Model类
	├─ pymonitor.py		<-- 对文件监控如果有修改不需要重启进程
	├─ schema.sql		<-- 简单的sql脚本，用于创建database表，项目ORM中就可以实现
	└─ test.py		<-- 项目过程中的测试文件

## 程序流程

在项目中我们使用logging模块打印程序运行信息，通过logging我们可以方便的了解程序大致流程

### 服务器初始化

开始运行webapp我们可以在控制台上看到如下信息：

```
(env) h@h:~/python3-project/python3-webapp/www$ python3 pymonitor.py app.py
[Monitor] Watch directory /home/h/python3-project/python3-webapp/www...
[Monitor] Start process python app.py...
INFO:root:found Model:User (table:users)
INFO:root:found mapping：     admin ==> <BooleanField, boolean:None>
INFO:root:found mapping：      name ==> <StringField, varchar(50):None>
INFO:root:found mapping：     email ==> <StringField, varchar(50):None>
INFO:root:found mapping：    passwd ==> <StringField, varchar(50):None>
INFO:root:found mapping：        id ==> <StringField, varchar(50):None>
INFO:root:found mapping：     image ==> <StringField, varchar(500):None>
INFO:root:found mapping：created_at ==> <FloatField, real:None>
INFO:root:found Model:Blog (table:blogs)
INFO:root:found mapping：   content ==> <TextField, text:None>
INFO:root:found mapping：user_image ==> <StringField, varchar(500):None>
INFO:root:found mapping：      name ==> <StringField, varchar(50):None>
INFO:root:found mapping： user_name ==> <StringField, varchar(50):None>
INFO:root:found mapping：        id ==> <StringField, varchar(100):None>
INFO:root:found mapping：   summary ==> <StringField, varchar(200):None>
INFO:root:found mapping：created_at ==> <FloatField, real:None>
INFO:root:found mapping：   user_id ==> <StringField, varchar(50):None>
INFO:root:found Model:Comment (table:comments)
INFO:root:found mapping：   content ==> <TextField, text:None>
INFO:root:found mapping：user_image ==> <StringField, varchar(500:None>
INFO:root:found mapping： user_name ==> <StringField, varchar(50):None>
INFO:root:found mapping：   blog_id ==> <StringField, varchar(50):None>
INFO:root:found mapping：        id ==> <StringField, varchar(100):None>
INFO:root:found mapping：created_at ==> <FloatField, real:None>
INFO:root:found mapping：   user_id ==> <StringField, varchar(50):None>
INFO:root:create a database connection pool...
INFO:root:init jinja2...
INFO:root:set jinja2 template path: /home/h/python3-project/python3-webapp/www/templates
INFO:root:add route GET /api/blogs => api_blogs(page)
INFO:root:add route GET /api/comments => api_comments(page)
INFO:root:add route POST /api/blogs => api_create_blog(request, name, summary, content)
INFO:root:add route POST /api/blogs/{id}/comments => api_create_comment(id, request, content)
INFO:root:add route POST /api/blogs/{id}/delete => api_delete_blog(request, id)
INFO:root:add route POST /api/comments/{id}/delete => api_delete_comment(id, request)
INFO:root:add route GET /api/blogs/{id} => api_get_blog(id)
INFO:root:add route GET /api/users => api_get_users(page)
INFO:root:add route POST /api/users => api_register_user(name, email, passwd)
INFO:root:add route POST /api/blogs/{id} => api_update_blog(id, request, name, summary, content)
INFO:root:add route POST /api/authenticate => authenticate(email, passwd)
INFO:root:add route GET /blog/{id} => get_blog(id)
INFO:root:add route GET / => index(page)
INFO:root:add route GET /manage/ => manage()
INFO:root:add route GET /manage/blogs => manage_blogs(page)
INFO:root:add route GET /manage/comments => manage_comments(page)
INFO:root:add route GET /manage/blogs/create => manage_create_blog()
INFO:root:add route GET /manage/blogs/edit => manage_edit_blog(id)
INFO:root:add route GET /manage/users => manage_users(page)
INFO:root:add route GET /register => register()
INFO:root:add route GET /signin => signin()
INFO:root:add route GET /signout => signout(request)
INFO:root:add static /static/ => /home/h/python3-project/python3-webapp/www/static
INFO:root:server started at http://127.0.0.1:9000...
```

由日志可知, 服务器启动之后进行了以下初始化操作:

1. **记录文件更改情况**，通过系统API监控相关文件是否改动，若有文件修改就会自动重启进程，能够有效避免修改代码后重复手动执行

```
[Monitor] python source file changed: /home/h/python3-project/python3-webapp/www/app.py
[Monitor] Kill process [9240]...
[Monitor] Process ended with code -9
[Monitor] Start process python app.py...
```
2. **建立model**, 简单点说就是建立python中的`类`与数据库中的`表`的映射关系
3. **创建全局数据库连接池**, 按廖老师的说法, 这是为了使每个http请求都可以从连接池中直接获取数据库连接, 而不必频繁地打开关闭数据库连接. 现在你真的意识到`orm.py`的重要性了吗? 很重要, 与数据打交道的活在其中都做了定义
3. **初始化jinja2引擎, 并设置模板的路径**, 主要是初始化了`jinja2 env`(环境), 并将`jinja2 env`绑定到`webapp`的`__templating__`属性上. 这是因为在初始化`jinja2 env`时, 指定了加载器(`loader`)为文件系统加载器(`FileSystemLoader`).
4. **注册处理器(handler)** `事务处理`的三要素: `方法(http method)` &  `路径(path)` & `处理函数(func)`. 将三者连起来看就是, 将对某路径的某种http请求交给某个函数处理, 而该函数就称为某路径上某种请求的处理器(handler).
5. **加载静态资源**
6. **创建服务器对象, 并绑定到socket**


### 服务器响应请求

当客户端随机提交一个请求时webapp又抛出一些响应的信息:

```
INFO:root:Request: GET /
INFO:root:check user: GET /
INFO:root:Response handler...
INFO:root:call with args: {}
INFO:root:[SQL sentence]：select count(id) _num_ from `blogs`
INFO:root:rows returned：1
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET / HTTP/1.1" 200 4662 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/css/uikit.min.css
INFO:root:check user: GET /static/css/uikit.min.css
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/css/uikit.min.css HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/css/uikit.gradient.min.css
INFO:root:check user: GET /static/css/uikit.gradient.min.css
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/css/uikit.gradient.min.css HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/css/awesome.css
INFO:root:check user: GET /static/css/awesome.css
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/css/awesome.css HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/js/sticky.min.js
INFO:root:check user: GET /static/js/sticky.min.js
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/js/sticky.min.js HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/js/jquery.min.js
INFO:root:check user: GET /static/js/jquery.min.js
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/js/jquery.min.js HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/js/awesome.js
INFO:root:check user: GET /static/js/awesome.js
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/js/awesome.js HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/js/uikit.min.js
INFO:root:check user: GET /static/js/uikit.min.js
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/js/uikit.min.js HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/js/vue.min.js
INFO:root:check user: GET /static/js/vue.min.js
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/js/vue.min.js HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/js/sha1.min.js
INFO:root:check user: GET /static/js/sha1.min.js
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:57 +0000] "GET /static/js/sha1.min.js HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
INFO:root:Request: GET /static/fonts/fontawesome-webfont.woff
INFO:root:check user: GET /static/fonts/fontawesome-webfont.woff
INFO:root:Response handler...
INFO:aiohttp.access:127.0.0.1 - - [26/Jul/2017:13:01:58 +0000] "GET /static/fonts/fontawesome-webfont.woff HTTP/1.1" 304 173 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
```
由日志可知, 客户端请求之后服务器进行了以下响应操作:

1. **服务器响应**，由中间件定制请求处理，接收一个`Request`对象并返回`Response`对象，通过解析url发送相应的响应信息.
2. **提取数据**, 在模板中将所有响应信息从数据库中提取出来
3. **加载前端模板**, 将`jinja2 env`从`webapp`的`__templating__`属性上取出，加载并提交给客户端，最后由jinja2渲染出前端页面



仔细看, 你会发现, 从上到下的过程就是一个实现`MVC`模型的过程: `建立model` -> `构建前端视图` -> `注册处理控制`.





## 参考资料


***[stackoverflow python](http://stackoverflow.com/questions/tagged/python?page=2&sort=votes&pagesize=15)***

- [What is a metaclass in Python?](http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python)
- [What is the difference between @staticmethod and @classmethod in Python?](http://stackoverflow.com/questions/136097/what-is-the-difference-between-staticmethod-and-classmethod-in-python)
- [What does the “yield” keyword do in Python?](http://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python)
- [In practice, what are the main uses for the new “yield from” syntax in Python 3.3?](http://stackoverflow.com/questions/9708902/in-practice-what-are-the-main-uses-for-the-new-yield-from-syntax-in-python-3)

【参考教程】：
【[Python3教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)】
【[python官方手册](https://docs.python.org/3/tutorial/index.html)】
