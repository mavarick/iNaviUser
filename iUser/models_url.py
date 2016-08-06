# encoding:utf8
from __future__ import unicode_literals

from django.db import models
from django.shortcuts import get_object_or_404
from django.db import connection, transaction

# Create your models here.
import pdb

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import BaseUserManager

from tools import dt_format, get_hash_id
from url_tools import std_url

from config import USER_URL_TABLE_NAME, MAX_USERNAME_LENGTH, DEFAULT_USERNAME

from iUserTag.models import tag_api, TagHandler
from iUserTopic.models import topic_api
from iUrl.models import url_api


class UserUrl(models.Model):
    id = models.AutoField(primary_key=True, db_column='user_url_id')
    username = models.CharField(max_length=100, null=False, default="nemo")
    # catename = models.CharField(max_length=100, null=False, default=DEFAULT_USER_CATE)
    # 不要加 catename,因为这样在移动的时候会变的很复杂!

    url_id = models.CharField(max_length=128, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, default="")
    topic_id = models.IntegerField(default=0)

    score = models.IntegerField(default=0)  # 自己的评分, 关注度

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = USER_URL_TABLE_NAME

    def get_info(self):
        return dict(id=self.id, username=self.username,
                    url_id=self.url_id, name=self.name, score=self.score,
                    topic_id=self.topic_id, last_update_time=dt_format(self.last_update_time),
                    created_time=dt_format(self.created_time))


class UserUrlApi(object):
    def __init__(self, user_url_model, url_api, topic_api, tag_api):
        self.model = user_url_model
        self.table_name = self.model._meta.db_table
        self.url_api = url_api
        self.topic_api = topic_api
        self.tag_api = tag_api

    def get(self, user_url_id):
        user_url_obj = get_object_or_404(self.model, id=user_url_id)
        user_url_info = user_url_obj.get_info()
        url_id = user_url_info['url_id']
        url_info = self.url_api.get(url_id)
        tags_info = self.tag_api.search_target(user_url_id)
        user_url_info['url_info'] = url_info
        user_url_info['tags'] = tags_info
        return user_url_info

    def add(self, url, username, name="", tags="", topic_id=None, score=5, **kwargs):
        url = url.strip()
        if not url:
            raise Exception("url is empty")
        #
        if not topic_id:
            topic_id = self.topic_api.get_favor_id(username)
        # add url table
        url = std_url(url)
        url_info = self.url_api.add(dict(url=url, username=username))
        url_id = url_info['id']

        # add user url table
        data_dict = dict(username=username, url_id=url_id,
                         topic_id=topic_id, score=score, name=name)
        data_dict.update(kwargs)
        user_url_obj, created = self.model.objects.get_or_create(username=username,
                        topic_id=topic_id, url_id=url_id, defaults=data_dict)
        user_url_id = user_url_obj.id

        # add tags
        tag_lists = TagHandler.split(tags)
        self.tag_api.add_target(user_url_id, tag_lists)

        user_url_info = self.get(user_url_id)
        return user_url_info

    # 更新url,主要包括更新: url地址,name,tags,score,分类
    def update_user_url(self, username, user_url_id, url=None, name=None, tags=None, topic_id=None, score=None):
        user_url_obj = self.model.objects.get(id=user_url_id)
        if url is not None:
            url = url.strip()
        url_id = user_url_obj.url_id
        if url:
            url = std_url(url)
            url_info = self.url_api.add(dict(url=url, username=username))
            url_id = url_info['id']
            user_url_obj.url_id = url_id
        # url_info = self.url_api.get_or_create(url_id)
        if name:
            user_url_obj.name = name
        if topic_id:
            user_url_obj.topic_id = topic_id
        if score is not None:
            user_url_obj.score = score
        user_url_obj.save()
        if tags is not None:
            tag_lists = TagHandler.split(tags)
            self.tag_api.delete_target(user_url_id)
            tag_objs = self.tag_api.add_target(user_url_id, tag_lists)

        user_url_info = self.get(user_url_id)
        return user_url_info

    def delete_user_url(self, user_url_id, username):
        # 这个里面只是放置在了回收站里面
        user_url_obj = self.model.objects.get(id=user_url_id)
        # 删除 tags
        user_url_obj.topic_id = self.topic_api.get_trash_id(username)
        user_url_obj.save()
        # self.tag_api.delete_target(user_url_id)
        # user_url_obj.delete()

    def delete_topic_urls(self, username, topic_id):
        # 删除一个topic下面的所有连接
        cnt = self.model.objects.filter(username=username, topic_id=topic_id).delete()
        return cnt

    def truncate_topic(self, username, topic_id):
        # 清空一个分类,直接删除,不保留到垃圾箱
        children = self.topic_api.get_total_children(username, topic_id)
        cnt_topics = len(children)
        cnt_urls = 0
        for child in children:
            cnt = self.delete_topic_urls(username, child.child_id)
            cnt_urls += cnt
            child.delete()
        return cnt_topics, cnt_urls

    def truncate_trash(self, username):
        trash_id = self.topic_api.get_trash_id()
        self.truncate_topic(username, trash_id)

    # 获得topic下所有的子分类
    def get_children_topics(self, username, topic_id):
        topics_info = self.topic_api.get_children_tree(username, topic_id)
        # 返回是json格式.
        return topics_info

    def get_cates_topics(self, username):
        cates = self.topic_api.get_cates(username)
        cates_info = []
        for cate in cates:
            name = cate['name']
            topic_id = cate['child_id']
            user_cate_info = self.get_children_topics(username, topic_id=topic_id)
            cates_info.append(user_cate_info)
        return cates_info

    # # 获得某一单一分类对应的urls信息
    def get_topic_urls(self, username, topic_id):
        # 获得某个已topicid的urls
        user_url_objs = self.model.objects.filter(username=username, topic_id=topic_id)
        user_url_infos = [t.get_info() for t in user_url_objs]
        for user_url_info in user_url_infos:
            user_url_id = user_url_info['id']
            url_id = user_url_info["url_id"]
            url_info = self.url_api.get(url_id)
            user_url_info['url_info'] = url_info
            # tags
            user_url_tag_info = self.tag_api.search_target(user_url_id)
            user_url_info['user_tag_infos'] = user_url_tag_info
        return user_url_infos

    # 获得topics下完整的格式信息, 包含topic, url, tags
    def get_topic_total_info(self, username, topic_id):
        topic_info = self.topic_api.get_children_tree(username, topic_id)

        def _get_tree_info(topic_info):
            topic_id = topic_info['child_id']
            user_urls_info = self.get_topic_urls(username, topic_id)
            topic_info['user_url_infos'] = user_urls_info
            for sub_topic_info in topic_info['sub']:
                # 获得url信息
                _get_tree_info(sub_topic_info)
        _get_tree_info(topic_info)
        return topic_info

    # # 获取用户的所有的主题信息
    # def get_cates_total_info(self, username):
    #     catenames = self.topic_api.get_cates(username)
    #     user_info = []
    #     for catename in catenames:
    #         user_cate_info = self.get_topic_total_info(username, catename, topic_id=self.topic_api.root_id)
    #         user_info.append(user_cate_info)
    #     return user_info

    # 获取某一个分类下所有的urls列表, 比如首页的那个网址导航
    def get_topic_total_urls(self, username, topic_id):
        topic_info = self.get_topic_total_info(username, topic_id)
        url_infos = []

        def _get_topic_total_urls(topic_info):
            sub_url_info = topic_info['user_url_infos']
            url_infos.extend(sub_url_info)
            for sub_topic_info in topic_info['sub']:
                _get_topic_total_urls(sub_topic_info)
        _get_topic_total_urls(topic_info)
        return url_infos

    # 获得最近添加的urls
    def get_recent_urls(self, username, size=10):
        if size:
            results = self.model.objects.filter(username=username).order_by("-last_update_time")[0:size]
        else:
            results = self.model.objects.filter(username=username).order_by("-last_update_time").all()
        return [self.get(t.id) for t in results]

    # 用来给find板块设计的功能
    def get_find_urls(self, size=30):
        if size:
            results = self.model.objects.order_by("-last_update_time")[0:size]
        else:
            results = self.model.objects.order_by("-last_update_time").all()
        return [self.get(t.id) for t in results]

    def add_topic(self, *args, **kargs):
        raise NotImplementedError("直接调用topic的api进行更改")

    def update_topic(self, username, cate_name, topic_id):
        raise NotImplementedError("直接调用topic的api进行更改")

    # # 删除topic
    # def delete_topic(self, username, catename, topic_id, force=True):
    #     # 如果是force,那么永久删除 user_url_id
    #     if topic_id == self.topic_api.trash_id:
    #         raise Exception("垃圾箱不能删除")
    #     # 抽取所有的 user_url_ids
    #     user_url_infos = self.get_topic_total_urls(username, catename, topic_id)
    #     # 把所有的user_url_id放到未分类的名下
    #     trash_id = self.topic_api.trash_id
    #
    #     result = []
    #     if force:
    #         ids = [t['id'] for t in user_url_infos]
    #         self.model.objects.filter(id__in=ids).delete()
    #     else:
    #         for user_url_info in user_url_infos:
    #             user_url_id = user_url_info['id']
    #
    #             new_user_url_info = self.update_user_url(username, catename, user_url_id, topic_id=trash_id)
    #             result.append(new_user_url_info)
    #
    #     if not (topic_id == self.topic_api.root_id):
    #         self.topic_api.delete()
    #
    #     return result

    def add_cate(self, username):
        raise NotImplementedError("直接调用topic的api进行更改")

    def update_cate(self, username, catename):
        # 对cate的自身属性的操作
        raise NotImplementedError()

    def get_topic_tree_stat(self, username, topic_id):
        topic_tree = self.topic_api.get_children_tree(username, topic_id)
        stat_info = dict(total_urls_cnt=0, total_sub_topics_cnt=0)

        def _f(topic_info, stat_info):
            topic_id = topic_info['child_id']
            # 返回子链接数量, 最后更新时间等 等
            topic_urls_cnt = self.model.objects.filter(username=username, topic_id=topic_id).count()
            sub_topics_cnt = len(topic_info['sub'])
            stat_info['total_urls_cnt'] += topic_urls_cnt
            stat_info['total_sub_topics_cnt'] += sub_topics_cnt
            for sub_topic_info in topic_info['sub']:
                _f(sub_topic_info, stat_info)
        _f(topic_tree, stat_info)
        return stat_info

    # def get_cates_stat(self, username):
    #     # 获得所有的cates
    #     cates = self.topic_api.get_cates(username)
    #     cates_info = []
    #     for cate in cates:
    #         topic_id = cate['child_id']
    #         cate_info = self.get_topic_tree_stat(username, topic_id)
    #         name = cate['name']
    #         cates_info.append((cate, cate_info))
    #     # dict(total_urls_cnt=0, total_sub_topics_cnt=0)
    #     return cates_info

    def delete_cate(self, username, topic_id, force=False):
        # root_id = self.topic_api.root_id
        # self.truncate_topic(username, catename, root_id, force=True)
        result = self.topic_api.delete_topic(username, topic_id, force=force)
        return result

    def delete_user(self, username):
        self.model.objects.filter(username=username).delete()
        self.topic_api.delete_user(username)

    def load_bookmark_tree(self, bookmark_tree, username):
        def _load_bookmark_tree(tree, parent_id, username):
            topic_name = tree['name']
            topic_info = self.topic_api.get_topic_id(username=username, parent_id=parent_id, name=topic_name)
            topic_id = topic_info['child_id']
            # 把urls保存下来
            url_infos = tree['url_infos']
            for url_info in url_infos:
                url_name = url_info['name']
                url = url_info['url']
                created_time = url_info['created_time']
                last_update_time = url_info['last_update_time']
                info = url_info.get('info', "")
                url_info = self.add(username=username, url=url, name=url_name, topic_id=topic_id,
                         created_time=created_time, last_update_time=last_update_time)
                print "loaded", url_info
            # 建立子的topic,然后迭代进行
            for sub_topic_info in tree['sub']:
                _load_bookmark_tree(sub_topic_info, topic_id, username)

        root_id = self.topic_api.get_root_id(username)
        _load_bookmark_tree(bookmark_tree, root_id, username)



# def wrap_topics_tree(tree):
#     id = tree['child_id']
#     name = tree['name']
#     html = ['<li class="accordion-navigation"><a href="#topic_{0}">{1}</a>'.format(id, name)]
#     html.append('<div id="topic_{0}" class="content active">'.format(id))
#     children = tree['sub']
#     for child in children:
#         html.append("<div>")
#         html.append('<ul class="accordion" data-accordion>')
#         html.append(wrap_topics_tree(child))
#         html.append("</ul>")
#         html.append("</div>")
#
#     html.append('</div>')
#     return ''.join(html)
#
#
# def wrap_topics_as_select(tree, level=0):
#     id = tree['child_id']
#     name = tree['name']
#     html = ['<option value="{0}">{1}{2}</option>'.format(id, "-"*level, name)]
#     children = tree['sub']
#     for child in children:
#         html.append(wrap_topics_as_select(child, level+1))
#     return ''.join(html)
#
#
# def wrap_topics_urls(tree, topics_urls):
#     id = tree['child_id']
#     name = tree['name']
#     html = ['<li class="accordion-navigation"><a href="#topic_{0}">{1}</a>'.format(id, name)]
#     html.append('<div id="topic_{0}" class="content active">'.format(id))
#     url_infos = topics_urls.get(id, [])
#     for url_info in url_infos:
#         html.append("<div><a href=''>{0}</a></div>".format(url_info['url_info']['url']))
#
#     children = tree['sub']
#     for child in children:
#         html.append("<div>")
#         html.append('<ul class="accordion" data-accordion>')
#         html.append(wrap_topics_urls(child, topics_urls))
#         html.append("</ul>")
#         html.append("</div>")
#
#     html.append('</div>')
#     return ''.join(html)


user_url_api = UserUrlApi(UserUrl, url_api=url_api, topic_api=topic_api, tag_api=tag_api)
