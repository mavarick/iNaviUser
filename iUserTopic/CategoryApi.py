# encoding:utf8
from django.shortcuts import get_object_or_404

import pickle
from django.db import connection, transaction
import pdb

from config import DEFAULT_ROOT_ID, DEFAULT_ROOT_NAME, \
    DEFAULT_TRASH_ID, DEFAULT_TRASH_NAME, DEFAULT_CATE_NAME, SITE_CATE_NAME
    # DEFAULT_UNKNOWN_ID, DEFAULT_UNKNOWN_NAME, DEFAULT_CATE_NAME

""" 设计原则:
1, 暂时基于django设计;
2, 尽量与数据库直接打交道;
3, 分类系统体系;
"""


class CategoryApi(object):
    def __init__(self, category_model, user_base_model):
        # category_model: 类别的model数据
        # func_get_info: 输入一个obj, 返回的dict数据
        self.model = category_model
        self.user_base_model = user_base_model
        self.table_name = self.model._meta.db_table
        self.base_table_name = self.user_base_model._meta.db_table
        self.root_name = DEFAULT_ROOT_NAME
        self.trash_name = DEFAULT_TRASH_NAME
        self.favor_cate_name = DEFAULT_CATE_NAME
        self.site_cate_name = SITE_CATE_NAME

    def init(self, username):
        # 创建 根节点
        root_obj, flag = self.model.objects.get_or_create(username=username, name=self.root_name)
        root_id = root_obj.child_id
        root_obj.parent_id = 0
        root_obj.save()
        # 创建垃圾桶节点, 单独创建节点
        trash_obj, flag = self.model.objects.get_or_create(username=username, name=self.trash_name, defaults=dict(score=0))
        trash_id = trash_obj.child_id
        # 创建默认收藏夹
        favor_obj, flag = self.model.objects.get_or_create(username=username, name=self.favor_cate_name, parent_id=root_id)
        favor_id = favor_obj.child_id
        site_obj, flag = self.model.objects.get_or_create(username=username, name=self.site_cate_name, parent_id=root_id)
        site_id = site_obj.child_id
        # 插入到user_topic_base
        obj, created = self.user_base_model.objects.get_or_create(username=username, defaults=dict(root_id=root_id,
                                          trash_id=trash_id, favor_id=favor_id, site_id=site_id))
        return obj.get_info()

    def exist_user(self, username):
        return self.user_base_model.objects.filter(username=username)

    def get_root_id(self, username):
        obj = self.user_base_model.objects.get(username=username)
        return obj.root_id

    def get_trash_id(self, username):
        obj = self.user_base_model.objects.get(username=username)
        return obj.trash_id

    def get_favor_id(self, username):
        # 用户的默认收藏夹
        obj = self.user_base_model.objects.get(username=username)
        return obj.trash_id

    def get_site_id(self, username):
        # 用户的默认收藏夹
        obj = self.user_base_model.objects.get(username=username)
        return obj.site_id

    def get_cates(self, username):
        # 获得一个用户的所有的categories
        root_id = self.get_root_id(username)
        cates = self.model.objects.filter(username=username, parent_id=root_id)
        # [{"catename": 'nemo'}, .. ]
        cates = [t.get_info() for t in cates]
        return cates

    def exists_cate(self, username, catename):
        root_id = self.get_root_id(username)
        objs = self.model.objects.filter(username=username, name=catename, parent_id=root_id)
        return objs

    def add_cate(self, username, catename, info="", score=5):
        # type=0 表示默认的导航板
        # 添加 一个新的分类, 任何一个新的分类的根节点都为 ROOT
        # 同时增加未分类 节点, 任何的未分类 节点的内容
        objs = self.exists_cate(username, catename)
        if objs:
            raise Exception("username[%s], catename:[%s] already exists"%(username, catename))
        root_id = self.get_root_id(username)
        obj = self.model.objects.create(name=catename, parent_id=root_id, username=username)
        obj.save()
        return obj.get_info()

    def add(self, username, name, parent_id, info="", score=50, **kwargs):
        # 查看这个节点是否存在,添加 一个节点
        exist_objs = self.model.objects.filter(name=name, parent_id=parent_id)
        if exist_objs:
            raise Exception("node[name:{}, parent_id:{}] already exists".format(name, parent_id))
        obj = self.model.objects.create(name=name, parent_id=parent_id, info=info, score=score, username=username, **kwargs)
        return obj.get_info()

    def get(self, username, topic_id):
        # 获得id的信息
        obj = get_object_or_404(self.model, child_id=topic_id)
        # obj = self.model.objects.get(username=username, child_id=topic_id)
        return obj.get_info()

    def get_topic_id(self, username, parent_id, name):
        parent_id = int(parent_id)
        obj, created = self.model.objects.get_or_create(username=username, parent_id=parent_id, name=name)
        return obj.get_info()

    def get_topic_path(self, username, topic_id):
        topics_path = []
        while 1:
            topic_info = self.get(username, topic_id)
            topics_path.append(topic_info)
            parent_id = topic_info["parent_id"]
            if topic_id == parent_id or not parent_id:
                break
            topic_id = parent_id
        return topics_path

    def get_children_list(self, username, parent_id):
        # 获得父节点为parent_id的所有子节点信息
        children = self.model.objects.filter(username=username, parent_id=parent_id)
        data = []
        for child in children:
            data.append(self.model.get_info(child))
        return data

    def get_children_ids(self, username, parent_id):
        children = self.get_children_list(username, parent_id)
        return [t['child_id'] for t in children]

    def get_children_tree(self, username, parent_id):
        # 递归得到所有的子节点的信息
        info = self.get(username, parent_id)
        children = self.get_children_list(username, parent_id)
        info['sub'] = []
        for child in children:
            child_id = child['child_id']
            child_info = self.get_children_tree(username, child_id)
            info['sub'].append(child_info)
        info['sub'] = sorted(info['sub'], key=lambda x:(x['score'], x['created_time']), reverse=True)
        return info

    def get_total_children(self, username, parent_id):
        # 获得所有的child的obj的列表
        result = []

        def _get_children(username, parent_id, result):
            children = self.model.objects.filter(username=username, parent_id=parent_id)
            result.extend(children)
            for child in children:
                child_id = child.child_id
                _get_children(username, child_id, result)
        _get_children(username, parent_id, result)
        return result

    def update(self, username, child_id, new_info={}):
        # 把id的节点的父节点更改为parent_id
        user_base_info = self.user_base_model.objects.get(username=username)
        deny_ids = [user_base_info.root_id, user_base_info.trash_id,
                    user_base_info.favor_id, user_base_info.site_id]
        if int(child_id) in deny_ids:
            raise Exception("不能删除的分类!")
        item_obj = self.model.objects.get(username=username, child_id=child_id)
        name = new_info.get("name", None) or item_obj.name
        # 如果有parent_id,说明更改parent,那么检查是否有重复现象
        parent_id = new_info.get("parent_id", None)
        if parent_id and parent_id != item_obj.parent_id:
            # 移动 分类
            exist_objs = self.model.objects.filter(username=username, name=name, parent_id=parent_id)
            if exist_objs:
                raise Exception("node [name:{0}] with parent_id[{1}] already existed".format(
                    name, parent_id
                ))
        for k, v in new_info.iteritems():
            setattr(item_obj, k, v)
        item_obj.save()
        return self.model.get_info(item_obj)

    def update_parent(self, username, child_id, parent_id):
        # 把id的节点的父节点更改为parent_id
        self.update(username, child_id, new_info=dict(parent_id=parent_id))

    def delete_topic(self, username, child_id, force=False):
        # 删除一条topic
        # 删除整个topic的方法是: 先删除关联的url,然后删除每一条topics
        user_base_info = self.user_base_model.objects.get(username=username)
        deny_ids = [user_base_info.root_id, user_base_info.trash_id,
                    user_base_info.favor_id, user_base_info.site_id]
        if child_id in deny_ids:
            raise Exception("不能删除的分类")
        obj = self.model.objects.get(username=username, child_id=child_id)
        # 移动到垃圾桶
        if not force:
            self.update(username, child_id, new_info=dict(parent_id=user_base_info.trash_id))
        else:
            obj.delete()
        return

    def delete_user(self, username):
        result = self.model.objects.filter(username=username).all().delete()
        result = self.user_base_model.objects.filter(username=username).all().delete()
        return result

    #deprecated
    def dump_to_txt(self, file_path):
        # 把数据库的信息保存到文件
        dict_rows = self.model.objects.values()
        num = len(dict_rows)
        fp = open(file_path, 'w')
        pickle.dump(dict_rows, fp)
        # print >>fp, json.dumps(dict_rows)
        print "dump to file:[{0}], num:[{1}]".format(file_path, num)

    #deprecated
    def load_from_txt(self, file_path):
        # 把本地数据 load进入数据库
        fp = open(file_path)
        rows = pickle.load(fp)
        # rows = json.loads(data)
        num = dict(created=0, existed=0)
        for row in rows:
            id = row['id']
            obj, created = self.model.objects.get_or_create(id=id, defaults=row)
            if created:
                num['created'] +=1
            else:
                num['existed'] +=1
        print "load from file: [{0}], total line: [{1}], existd: [{2}], created: [{3}]".format(
            file_path, num['existed']+num['created'], num['existed'], num['created']
        )



''' test >> python manage.py shell
from category.models import Category
from category.CategoryApi import CategoryApi
ca = CategoryApi(Category)
username ='nemo'
catename='nemo'
ca.add_cate(username, catename)

ca.exists_cate(username, catename)

root_obj = ca.get_root(username, catename)

root_id = root_obj['child_id']
obj = ca.add(username, catename, "学习", root_id)
obj = ca.add(username, catename, "python", obj["child_id"])

ca.get_children_tree(username, catename, 100)

ca.get(username, catename, root_id)
ca.get_by_name(username, catename, "学习")

ca.get_children_tree(username, catename, 101)
ca.update(username, catename, 102, {"name": "学习python"})

ca.update_parent(username, catename, 102, 99)


obj = ca.add(username, catename, "学习html", 101)
obj = ca.add(username, catename, "golang", 102)

ca.delete(username, catename, 2)  # raise
ca.delete(username, catename, 102)
ca.delete(username, catename, 104)

ca.dump_to_txt("./cate.d")
ca.load_from_txt("./cate.d")

'''









