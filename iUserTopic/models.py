# encoding:utf8
from __future__ import unicode_literals

from django.db import models
from tools import dt_format
from config import CATE_TABLE_NAME, USER_BASE_TABLE

from CategoryApi import CategoryApi

# Create your models here.
USERNAME_MAX_LENGTH = 50
CATENAME_MAX_LENGTH = 50
NODENAME_MAX_LENGTH = 50


# 用来存放cate信息, 其中(username, catename) 是唯一的,不行Category表中不是唯一的
# class UserCateInfo(models.Model):
#     id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=USERNAME_MAX_LENGTH, null=False)
#     catename = models.CharField(max_length=CATENAME_MAX_LENGTH, null=False)
#
#     info = models.TextField(null=False, default="")  # 节点的相关信息
#     score = models.IntegerField(null=False, default=50)  # [0, 100]
#     type = models.IntegerField(default=0)  # 默认=0, 其他为别的值, 默认导航板不能删除
#
#     status = models.IntegerField(default=0)
#     last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
#     create_time = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         db_table = USER_CATE_TABLE_NAME
#
#     def get_info(obj): # obj=self
#         id = obj.id
#         username = obj.username
#         catename = obj.catename
#         info = obj.info
#         score = obj.score
#         status = obj.status
#         last_update_time = dt_format(obj.last_update_time)
#         create_time = dt_format(obj.create_time)
#
#         return dict(id=id, username=username, catename=catename, info=info,
#                     score=score, status=status, last_update_time=last_update_time, create_time=create_time
#                     )


class UserTopicBase(models.Model):
    child_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=USERNAME_MAX_LENGTH, db_column="username", unique=True)
    root_id = models.IntegerField(null=False, blank=False)  # 存放用户的根id
    trash_id = models.IntegerField(null=False, blank=False) # 存放用户的垃圾桶id
    favor_id = models.IntegerField(null=False, blank=False) # 存放用户的网络书签
    site_id = models.IntegerField(null=False, blank=False) # 存放用户的常用个人导航

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = USER_BASE_TABLE

    def get_info(self):
        username = self.username
        root_id = self.root_id
        trash_id = self.trash_id

        # status = self.status
        # last_update_time = dt_format(self.last_update_time)
        # create_time = dt_format(self.create_time)

        return dict(username=username, root_id=root_id, trash_id=trash_id)


# 用来存放对应的topic信息
# unique: (username, parent_id, name)
# unique: (username, child_id), 即同一个用户同一个目录下面不会出现相同的topic名字
class Category(models.Model):
    # 这个地方应该存放关系信息,以及关系之间的信息
    child_id = models.AutoField(primary_key=True, db_column="child_id")
    username = models.CharField(max_length=USERNAME_MAX_LENGTH, null=False)
    # 加入username,来获取这个用户的所有topic, 这样可以省很多事情!
    # catename = models.CharField(max_length=CATENAME_MAX_LENGTH, null=False)
    parent_id = models.IntegerField(null=True)  # 父节点的id, 父节点的username和cate_name应该和子节点一致
    name = models.CharField(max_length=NODENAME_MAX_LENGTH, null=False)  # 节点的名字

    info = models.TextField(null=False, default="")  # 节点的相关信息
    score = models.IntegerField(null=False, default=50)  # [0, 100]

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = CATE_TABLE_NAME

    def get_info(obj): #obj=self
        name = obj.name
        username = obj.username
        child_id = obj.child_id
        parent_id = obj.parent_id
        info = obj.info
        score = obj.score
        status = obj.status
        last_update_time = dt_format(obj.last_update_time)
        create_time = dt_format(obj.create_time)

        return dict(name=name, username=username, child_id=child_id, parent_id=parent_id, info=info,
                    score=score, status=status, last_update_time=last_update_time, created_time=create_time
                    )


# topic_api = CategoryApi(Category, UserCateInfo)
topic_api = CategoryApi(Category, UserTopicBase)
from config import ADMIN_USERNAME
topic_api.init(ADMIN_USERNAME)

#
# class CategoryNode(models.Model):
#     id = models.IntegerField(primary_key=True)
#     info = models.TextField(null=False, default="")
#
#     status = models.IntegerField(default=0)
#     last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
#     created_time = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         db_table = "node"
#
#     @staticmethod
#     def get_info(obj):
#         id = obj.id
#         info = obj.info
#
#         status = obj.status
#         last_update_time = dt_format(obj.last_update_time)
#         create_time = dt_format(obj.create_time)
#
#         return dict(id=id, info=info, status=status,
#                     last_update_time=last_update_time, create_time=create_time)
