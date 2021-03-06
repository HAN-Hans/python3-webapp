#!/usr/bin/python3
# -*- coding:utf-8 -*-

""" ORM(Object Relational Mapping） 对象关系映射

用来把对象模型表示的对象映射到基于SQL的关系模型数据库结构中去。
这样，我们在具体的操作实体对象的时候，就不需要再去和复杂的SQL语句打交道，
只需简单的操作实体对象的属性和方法。ORM技术是在对象和关系之间提供了一条桥梁，
前台的对象型数据和数据库中的关系型的数据通过这个桥梁来相互转化。
"""


import asyncio
import logging
import aiomysql


# 这个函数的作用是输出信息，让你知道这个时间点程序在做什么
def log(sql, args=()):
    logging.info("[SQL sentence]：%s" % sql)


# 这个函数在定义元类时被引用，作用是创建一定数量的占位符
def create_args_string(num):
    l = []
    for n in range(num):
        l.append('?')
    # 比如说num=3，那l就是['?','?','?']，通过下面这句代码返回一个字符串'?,?,?'
    return ', '.join(l)


# ======================================创建连接池================================

# 这个函数将来会在app.py的init函数中引用
# 目的是为了让每个HTTP请求都能从连接池中直接获取数据库连接
# 避免了频繁关闭和打开数据库连接
# 连接池由全局变量__pool存储，缺省情况下将编码设置为utf8(不是utf-8)，自动提交事务
async def create_pool(loop, **kw):
    logging.info("create a database connection pool...")
    # 声明变量__pool是一个全局变量，如果不加声明，__pool就会被默认为一个私有变量
    global __pool
    # 调用一个子协程来创建全局连接池，create_pool的返回值是一个pool实例对象
    __pool = await aiomysql.create_pool(
        # 下面就是创建数据库连接需要用到的一些参数，从**kw（关键字参数）中取出来
        # kw.get的作用应该是，当没有传入参数是，默认参数就是get函数的第二项
        host=kw.pop("host", "localhost"),  # 数据库服务器位置，默认设在本地
        port=kw.pop("port", 3306),  # mysql的端口，默认设为3306
        user=kw.pop("user", "root"),  # 登陆用户名，通过关键词参数传进来
        password=kw.pop("password", None),  # 登陆密码，通过关键词参数传进来
        db=kw.pop("db", None),  # 当前数据库名
        charset=kw.pop("charset", "utf8"),  # 设置编码格式，默认为utf8
        autocommit=kw.pop("autocommit", True),  # 自动提交模式，设置默认开启
        maxsize=kw.pop("maxsize", 10),  # 最大连接数默认设为10
        minsize=kw.pop("minsize", 1),  # 最小连接数，默认设为1
        loop=loop  # 传递消息循环对象，用于异步执行
    )


# =================================以下是SQL函数处理区============================
# select和execute方法是实现其他Model类中SQL语句都经常要用的方法

# 将执行SQL的代码封装为select函数，调用的时候只要传入sql，和sql所需要的一些参数就好
# sql参数即为sql语句，args表示要搜索的参数
# size用于指定最大的查询数量，不指定将返回所有查询结果
@asyncio.coroutine
def select(sql, args, size=None):
    log(sql, args)
    # 声明全局变量，这样才能引用create_pool函数创建的__pool变量
    global __pool
    # 从连接池中获得一个数据库连接
    # 用with语句可以封装清理（关闭conn)和处理异常工作
    with (yield from __pool) as conn:
        # 等待连接对象返回DictCursor可以通过dict的方式获取数据库对象
        cur = yield from conn.cursor(aiomysql.DictCursor)
        # 设置执行语句，其中sql语句的占位符为？，而python为%s, 这里要做一下替换
        yield from cur.execute(sql.replace("?", "%s"), args or ())
        # 如果制定了查询数量，则查询制定数量的结果，如果不指定则查询所有结果
        if size:
            rs = yield from cur.fetchmany(size)     # 从数据库获取指定的行数
        else:
            rs = yield from cur.fetchall()          # 返回所有结果集
        # yield from cur.close
        logging.info("rows returned：%s" % len(rs))
        return rs                                   # 返回结果集

# execute()函数只返回结果数，不返回结果集，适用于insert, update, Delete这些语句


@asyncio.coroutine
def execute(sql, args):
    log(sql)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace("?", "%s"), args)
            affected = cur.rowcount     # 返回受影响的行数
            yield from cur.close()
        except BaseException as e:
            raise
        return affected


# ================================Field定义域区=================================
# 首先来定义Field类，它负责保存数据库表的字段名和字段类型

# 父定义域，可以被其他定义域继承
class Field(object):
    # 定义域的初始化，包括属性（列）名，属性（列）的类型，主键，默认值
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default  # 如果存在默认值，在getOrDefault()中会被用到

    # 定制输出信息为 类名，列的类型，列名
    def __str__(self):
        return "<%s, %s:%s>" % (self.__class__.__name__,
                                self.column_type,
                                self.name)

# 字符串域


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None,
                 ddl="varchar(100)"):
        super().__init__(name, ddl, primary_key, default)

# 整数域


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, "bigint", primary_key, default)

# 布尔数域


class BooleanField(Field):
    def __init__(self, name=None, primary_key=False, default=False):
        super().__init__(name, "boolean", primary_key, default)

# 浮点数域


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, "real", primary_key, default)

# 文本域


class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


# ================================ModelMetaclass===============================

# 编写元类，任何定义了__metaclass__属性或指定了metaclass的都会通过元类定义的构造方法构造类
class ModelMetaclass(type):
    # cls: 当前准备创建的类对象,相当于self
    # name: 类名,比如User继承自Model,当使用该元类创建User类时,name=User
    # bases: 父类的元组,bases=(Model,)
    # attrs: 属性(方法)的字典,比如User有__table__,id,等,就作为attrs的keys
    def __new__(cls, name, bases, attrs):
        # 排除Model类本身,因为Model类主要就是用来被继承的,其不存在与数据库表的映射
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        # 获取table名称
        tableName = attrs.get("__table__", None) or name
        logging.info("found Model:%s (table:%s)" % (name, tableName))
        # 获取所有定义域中的属性和主键
        mappings = dict()       # 用字典来储存类属性与数据库表的列的映射关系
        fields = []             # 用于保存除主键外的属性
        primaryKey = None       # 用于保存主键
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info("found mapping：%10s ==> %s" % (k, v))
                mappings[k] = v
                # 先判断找到的映射是不是主键
                if v.primary_key:
                    if primaryKey:  # 若主键已存在,又找到一个主键,将报错,每张表有且仅有一个主键
                        raise RuntimeError(
                            "Duplicate primary key for field:%s" % k)
                    primaryKey = k
                else:
                    fields.append(k)
        # 如果没有找到主键，也会报错
        if not primaryKey:
            raise RuntimeError("Primary key not found.")
        # 定义域中的key值已经添加到fields里了，就要在attrs中删除，避免重名导致运行时错误
        for k in mappings.keys():
            attrs.pop(k)
        # 将非主键的属性变形,放入escaped_fields中,方便sql语句的书写
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs["__mappings__"] = mappings        # 保存属性和列的映射关系
        attrs["__table__"] = tableName            # 表名
        attrs["__primary_key__"] = primaryKey   # 主键属性名
        attrs["__fields__"] = fields            # 除主键外的属性名

        # 构造默认的SELECT, INSERT, UPDATE, DELETE语句,以下都是sql语句
        attrs["__select__"] = "select `%s`, %s from `%s`" % \
            (primaryKey, ",".join(escaped_fields), tableName)
        attrs["__insert__"] = "insert into `%s` (%s, `%s`) values (%s)" % \
            (tableName, ",".join(escaped_fields), primaryKey,
                create_args_string(len(escaped_fields) + 1))
        attrs["__update__"] = "update `%s` set %s where `%s`=?" % (tableName, ",".join(
            map(lambda f: "`%s`=?" % (mappings.get(f).name or f), fields)), primaryKey)
        attrs["__delete__"] = "delete from `%s` where `%s`=?" % \
            (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


# ==================================Model基类区=================================

# 定义所有ORM映射的基类Model，使他既可以像字典那样通过[]访问key值，也可以通过.访问key值
# 元类自然是为了封装我们之前写的具体的SQL处理函数，从数据库获取数据
# ORM映射基类,通过ModelMetaclass元类来构造类
class Model(dict, metaclass=ModelMetaclass):
    # 这里直接调用了Model的父类dict的初始化方法，把传入的关键字参数存入自身的dict中
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    # 获取dict的值
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    # 设置dict的值
    def __setattr__(self, key, value):
        self[key] = value

    # 获取某个key具体的值即Value,如果不存在则返回None
    def getValue(self, key):
        # getattr(object, name[, default]) 根据name(属性名）返回属性值，默认为None
        return getattr(self, key, None)

    # 与上一个函数类似，但是如果这个属性与之对应的值为None时，就需要返回定义的默认值
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            # self.__mapping__在metaclass中，保存不同实例属性在Model基类中的映射关系
            # field是一个定义域!
            field = self.__mappings__[key]
            # 如果field存在default属性，那可以直接使用这个默认值
            if field.default is not None:
                # 如果field的default属性是callable(可被调用的)，
                # 就给value赋值它被调用后的值，如果不可被调用直接返回这个值
                value = field.default() if callable(field.default) \
                    else field.default
                logging.debug("using defaullt value for %s: %s" %
                              (key, str(value)))
                # 把默认值设为这个属性的值
                setattr(self, key, value)
        return value

    # ==============往Model类添加类方法，就可以让所有子类调用类方法=================

    # classmethod这个装饰器是类方法的意思，即可以不创建实例直接调用类方法
    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        # select `%s`, %s from `%s` where `%s`=?
        # select函数之前定义过，这里传入了三个参数分别是之前定义的 sql、args、size
        rs = yield from select("%s where `%s`=?" %
                               (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    # findAll() - 根据WHERE条件查找
    @classmethod
    @asyncio.coroutine
    def findAll(cls, where=None, args=None, **kw):
        # select `%s`, %s from `%s` where `%s` = ? Orderby `%s` limit ("?,?")
        sql = [cls.__select__]
        # 如果有where参数就在sql语句中添加字符串where和参数where
        if where:
            sql.append("where")
            sql.append(where)
        if args is None:  # 这个参数是在执行sql语句前嵌入到sql语句中的
            args = []
        # 如果有OrderBy参数就在sql语句中添加字符串OrderBy和参数OrderBy
        OrderBy = kw.get("OrderBy", None)
        if OrderBy:
            sql.append("OrderBy")
            sql.append(OrderBy)
        limit = kw.get("limit", None)
        if limit is not None:
            sql.append("limit")
            if isinstance(limit, int):
                sql.append("?")
                args.append(limit)
            if isinstance(limit, tuple) and len(limit) == 2:
                sql.append("?,?")
                args.extend(limit)  # extend()函数用于在列表末尾追加另一个序列
            else:
                raise ValueError("Invalid limit value: %s" % limit)
        rs = yield from select(" ".join(sql), args)
        return [cls(**r) for r in rs]

    # findNumber() - 根据WHERE条件查找，但返回的是整数，适用于select count(*)类型的SQL
    @classmethod
    @asyncio.coroutine
    def findNumber(cls, selectField, where=None, args=None):
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append("where")
            sql.append(where)
        rs = yield from select(" ".join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    # save、update、remove这三个方法需要管理员权限才能操作，
    # 所以不定义为类方法，需要创建实例之后才能调用

    @asyncio.coroutine
    def save(self):
        # 将除主键外的所有属性名添加到args这个列表中
        args = list(map(self.getValueOrDefault, self.__fields__))
        # 再把主键添加到这个列表的最后
        args.append(self.getValueOrDefault(self.__primary_key__))
        # insert into `%s` (%s, `%s`) values (%s)
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warning(
                "failed to insert record, affected rows: %s" %
                rows)

    @asyncio.coroutine
    def update(self):
        # 将参数中提供除主键外的属性名添加到args这个列表中
        args = list(map(self.getValue, self.__fields__))
        # 再把主键添加到这个列表的最后
        args.append(self.getValue(self.__primary_key__))
        # update `%s` set %s where `%s`=?
        rows = yield from execute(self.__update__, args)
        if rows != 1:
            logging.warning(
                'failed to update by primary key: affected rows: %s' % rows)

    @asyncio.coroutine
    def remove(self):
        args = [self.getValue(self.__primary_key__)]
        # delete from `%s` where `%s`=?
        rows = yield from execute(self.__delete__, args)
        if rows != 1:
            logging.warning(
                'failed to remove by primary key: affected rows: %s' % rows)
