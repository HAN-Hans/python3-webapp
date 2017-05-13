# python3-webapp
 Asesome Pyhthon3 WebApp 总结

***

##	#引言

这个项目是大概花了一个多月时间完成的，代码几乎全是照着[实战](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432170876125c96f6cc10717484baea0c6da9bee2be4000) 自己一个一个敲出来的. 期间我查阅了许多[资料](#reference), 几乎为每一行代码都加了详尽的注释.暂时这个个人博客还没有部署在服务器上，我打算在学习玩前端知识后将前端页面修改好后在部署到服务器上

##	#正文

***	开发环境***
python版本：python3.6.1		
异步框架：aiohttp
前端模板引擎:jinja2
数据库：MySQL5.6

***	项目结构***

    python3-webapp     <-- 根目录
	  ├─backup           <-- 备份目录			
	  ├─conf             <-- 配置文件
	  │  ├─nginx
	  │  └─supervisor
	  ├─ios              <-- 存放iOS App工程
	  │  └─AwesomeApp.xcodeproj
	  │      └─project.xcworkspace
	  └─www              <-- Web目录，存放.py文件
	      ├─static       <-- 存放静态文件
	      │  ├─css
	      │  │  └─addons
	      │  ├─fonts
	      │  ├─img
	      │  └─js
	      ├─templates    <-- 存放模板文件
	      └─__pycache__

## 部分学习材料

<p id="reference"></p>

- [e-satis在stackoverflow上的回答](http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python/6581949#6581949)
- [aiohttp官方文档](http://aiohttp.readthedocs.org/en/stable/web.html)
- [aiomysql官方文档](http://aiomysql.readthedocs.io/en/latest/index.html)
- [jinja2官方文档](http://jinja.pocoo.org/docs/latest/)
- [jinja2中文版文档](http://docs.jinkan.org/docs/jinja2/)(翻译不全, 不如看原版)



参考：[Python3教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)

