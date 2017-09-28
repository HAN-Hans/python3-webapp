#-*- coding:utf-8 -*-

'''
        models      模板
    有了ORM，我们就可以把Web App需要的3个表用Model表示出来,
    User:用户        Blog:博客        Comment:评论
    用于创建数据库表格的模板
'''

# uuid是python中生成唯一ID的库
import uuid, time
from orm import Model, StringField, BooleanField, FloatField, TextField


# 这个函数的作用是生成一个基于时间的独一无二的id，来作为数据库表中每一行的主键
def next_id():
    # time.time() 返回当前时间的时间戳(相对于1970.1.1 00:00:00以秒计算的偏移量)
    # uuid4()——由伪随机数得到，有一定的重复概率，该概率可以计算出来。
    return "%015d%s000" % (int(time.time()*1000), uuid.uuid4().hex)


# 这是一个用户名的表
class User(Model):
    __table__ = "users"

    id = StringField(primary_key = True, default = next_id(),
                     ddl = "varchar(50)")
    email = StringField(ddl = "varchar(50)")
    passwd = StringField(ddl = "varchar(50)")
    admin = BooleanField()
    name = StringField(ddl = "varchar(50)")
    image = StringField(ddl = "varchar(500)")
    created_at = FloatField(default = time.time)

# 这是一个博客的表
class Blog(Model):
    __table__ = "blogs"

    id = StringField(primary_key = True, default = next_id())
    user_id = StringField(ddl = "varchar(50)")
    user_name = StringField(ddl = "varchar(50)")
    user_image = StringField(ddl = "varchar(500)")
    name = StringField(ddl = "varchar(50)")
    summary = StringField(ddl = "varchar(200)")
    content = TextField()
    created_at = FloatField(default = time.time)

# 这是一个评论的表
class Comment(Model):
    __table__ = "comments"

    id = StringField(primary_key = True, default = next_id())
    blog_id = StringField(ddl = "varchar(50)")
    user_id = StringField(ddl = "varchar(50)")
    user_name = StringField(ddl = "varchar(50)")
    user_image = StringField(ddl = "varchar(500")
    content = TextField()
    created_at = FloatField(default = time.time)
