# Web-app 总结

# logging

`logging`模块是对应用程序或库实现一个灵活的事件日志处理系统

基本设置:
```python
logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='/tmp/test.log',  
                    filemode='w') 
```
输出:
``` log
cat /tmp/test.log   
Mon, 05 May 2014 16:29:53 test_logging.py[line:9] DEBUG debug message
```


日志级别大小关系为：CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
用basiconfig()函数设置logging的默认level为INFO

# json

json提供四个功能：dumps, dump, loads, load

1. dumps功能 将数据通过特殊的形式转换为所有程序语言都认识的字符串
```python
data = ['aa', 'bb', 'cc']
j_str = json.dumps(data) // '["aa", "bb", "cc"]'
```
2. loads功能 将json编码的字符串再转换为python的数据结构
```python
mes = json.loads(j_str) // ['aa', 'bb', 'cc']
```
3. dump功能 将数据通过特殊的形式转换为所有程序语言都认识的字符串，并写入文件
```python
with open('D:/tmp.json', 'w') as f:
    json.dump(data, f)
```
4. load功能 从数据文件中读取数据,并将json编码的字符串转换为python的数据结构
```python
with open('D:/tmp.json', 'r') as f:
    data = json.load(f)
```
   
**[注意]** json编码的格式几乎和python语法一致，略有不同的是：True会被映射为true,False会被映射为false,None会被映射为null，元组()会被映射为列表[]，因为其他语言没有元组的概念，只有数组，也就是列表。
```python
data = {'a':True, 'b':False, 'c':None, 'd':(1,2), 1:'abc'}
j_str = json.dumps(data) // '{"a": true, "c": null, "d": [1, 2], "b": false, "1": "abc"}'
```

# asyncio 

asyncio的编程模块实际上就是一个消息循环
我们从asyncio模块中直接获取一个eventloop（事件循环）的引用，
@asyncio.coroutine把一个generator标记为coroutine类型
然后，我们就把这个coroutine扔到EventLoop中执行

第一步是获取eventloop
get_event_loop() => 获取当前脚本下的事件循环，返回一个event loop对象
实现AbstractEventLoop（事件循环的基类）接口
如果当前脚本下没有事件循环，将抛出异常，get_event_loop()永远不会抛出None

# aiohttp

web.Application
    
    # middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理
    # 一个middleware可以改变URL的输入、输出，甚至可以决定不继续处理而直接返回
    # middleware的用处就在于把通用的功能从每个URL处理函数中拿出来，集中放到一个地方