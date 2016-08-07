# Create your views here.
#encoding:utf8

from django.shortcuts import render, render_to_response, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib import auth
from iUser.models import user_info_api
from utils.tag_handler import TagHandler
from iUserTopic.models import topic_api
from utils.tools import get_request_field
from models_url import user_url_api
from user_tools import get_user_info

# 显示改目录下的收藏内容和子文件夹
@login_required(login_url="/user/login/")
def show_topic(request, username, topic_id):
    user_info = user_info_api.get_info(username)
    topic_path = topic_api.get_topic_path(username, topic_id)
    topic_path.reverse()
    sub_topics = topic_api.get_children_list(username, topic_id)
    topic_urls = user_url_api.get_topic_urls(username, topic_id)

    template_file = "iUser/show_topic.html"
    return render(request, template_file, {"topic_path": topic_path, "sub_topics": sub_topics,
                                           "topic_urls": topic_urls, "user_info": user_info})


# 显示改目录下的收藏内容和子文件夹
@login_required(login_url="/user/login/")
def show_topics(request, username):
    user_info = user_info_api.get_info(username)
    template_file = "iUser/show_topics.html"
    topic_id = topic_api.get_root_id(username)
    topic_tree = topic_api.get_children_tree(username, topic_id)
    topics = wrap_topics_treetable(username, topic_tree)
    topics = "".join(topics)
    return render(request, template_file, {"user_info": user_info, "topics": topics})


# 显示改目录下的收藏内容和子文件夹
@login_required(login_url="/user/login/")
def update_topic(request, username, topic_id):
    user_info = user_info_api.get_info(username)
    if request.method == 'POST':
        name = get_request_field(request, "topic_name", must=True)
        parent_id = get_request_field(request, "topic_id", must=True)
        parent_id = int(parent_id)
        info = get_request_field(request, "info", must=False, default="")
        score = get_request_field(request, "score", must=False, default=5)
        new_info = dict(name=name, parent_id=parent_id, score=score, info=info)
        topic_info = topic_api.update(username=username, child_id=topic_id, new_info=new_info)
        return HttpResponseRedirect(reverse("user:show_topic", args=(username, parent_id)))

    topic_path = topic_api.get_topic_path(username, topic_id)
    topic_path.reverse()

    user_topic_info = topic_api.get(username, topic_id)

    topic_root_id = topic_api.get_root_id(username)
    user_topic_tree = topic_api.get_children_tree(username, topic_root_id)
    user_topic_select = wrap_as_select(user_topic_tree, target_id=user_topic_info['parent_id'], level=0)
    user_topic_select = ''.join(user_topic_select)
    template_file = "iUser/update_topic.html"
    return render(request, template_file, {"user_info": user_info, "topic_path": topic_path,
                                           "user_topic_info": user_topic_info, "user_topics": user_topic_select })


# 显示改目录下的收藏内容和子文件夹
@login_required(login_url="/user/login/")
def delete_topic(request, username, topic_id):
    user_topic_info = topic_api.get(username, topic_id)
    parent_id = user_topic_info['parent_id']
    topic_id = int(topic_id)
    topic_api.delete_topic(username, topic_id, force=True)
    return HttpResponseRedirect(reverse("user:show_topic", args=(username, parent_id)))


# 显示改目录下的收藏内容和子文件夹
@login_required(login_url="/user/login/")
def add_topic(request, username):
    user_info = user_info_api.get_info(username)
    if request.method == 'POST':
        name = get_request_field(request, "name", must=True)
        parent_id = get_request_field(request, "topic_id", must=True)
        parent_id = int(parent_id)
        info = get_request_field(request, "info", must=False, default="")
        score = get_request_field(request, "score", must=False, default=5)
        topic_info = topic_api.add(username=username, name=name, parent_id=parent_id, score=score, info=info)
        return HttpResponseRedirect(reverse("user:show_topics", args=(username, )))

    topic_root_id = topic_api.get_root_id(username)
    user_topic_tree = topic_api.get_children_tree(username, topic_root_id)
    user_topic_select = wrap_as_select(user_topic_tree, target_id=None, level=0)
    user_topic_select = ''.join(user_topic_select)
    template_file = "iUser/add_topic.html"
    return render(request, template_file, {"user_info": user_info, "user_topics": user_topic_select})


def wrap_as_select(topic_tree, target_id, level, span=20):
    html = []
    name = topic_tree['name']
    topic_id = topic_tree['child_id']
    space = " "*(level*5)
    if target_id == topic_id:
        html_str = "<option value='%s' style='margin-left:%spx;' selected>%s</option>"%(topic_id, span*level, name)
    else:
        html_str = "<option value='%s' style='margin-left:%spx;'>%s</option>"%(topic_id, span*level, name)
    html.append(html_str)
    for sub_topic in topic_tree['sub']:
        html.extend(wrap_as_select(sub_topic, target_id, level+1, span=span))
    return html


# 用来形成首页的展示效果 ->
def wrap_topics_treetable(username, cate_tree):
    html = []
    child_id = cate_tree['child_id']
    parent_id = cate_tree['parent_id']
    name = cate_tree['name']
    topic_url = reverse("user:show_topic", args=(username, child_id))
    created_time = cate_tree['created_time']
    url = reverse("user:show_topic", args=(username, child_id))
    html.append(
            "<tr data-tt-id='%s' data-tt-parent-id='%s'><td><span class='folder'>"
            "<a href='%s'>%s</a></span>"%(child_id, parent_id, url, name)
        )

    sub_topics = cate_tree['sub']

    for sub_topic in sub_topics:
        sub_html = wrap_topics_treetable(username, sub_topic)
        html.extend(sub_html)
    return html