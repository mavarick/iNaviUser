# encoding:utf8

from django.shortcuts import render, render_to_response, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from user_tools import get_user_info
from utils.tools import get_request_field
from utils.bookmark import parse_bookmark

from models_url import user_url_api, topic_api
from models import user_info_api


@login_required(login_url="/home/login/")
def show_urls(request, username):
    template_file = "iUser/latest.html"
    user_info = user_info_api.get_info(username)
    size = get_request_field(request, "size", must=False, default=20)
    size = int(size)
    username = user_info['username']

    # 最近收藏
    user_urls = user_url_api.get_recent_urls(username, size=size)

    return render(request, template_file, {"user_info": user_info, "user_urls": user_urls})


# @login_required(login_url="/home/login/")
def find(request):
    from views_topic import wrap_topics_treetable
    template_file = "iUser/find.html"

    # 最新收藏
    user_urls = user_url_api.get_find_urls(size=None)

    return render(request, template_file, {"user_info": user_info, "user_urls": user_urls})


@login_required(login_url="/home/login/")
def follow(request):
    from views_topic import wrap_topics_treetable
    template_file = "iUser/follow.html"
    follows = []
    user_urls = user_url_api.get_find_urls(size=20)
    return render(request, template_file, {"follows": follows, "user_urls": user_urls})


@login_required(login_url="/home/login/")
def show_user_info(request):
    from views_topic import wrap_topics_treetable
    template_file = "iUser/user_info.html"
    return render(request, template_file)


class FileForm(forms.Form):
    bookmark = forms.FileField()
@login_required(login_url="/home/login/")
def upload_bookmark(request, username):
    from views_topic import wrap_topics_treetable
    template_file = "iUser/upload_bookmark.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']

    if request.method == "POST":
        # 读取文件
        ff = FileForm(request.POST, request.FILES)
        if ff.is_valid():
            file = request.FILES.get('bookmark')
            data = file.read()
            book_marks_info = parse_bookmark(data)
            user_url_api.load_bookmark_tree(book_marks_info, username)
            return HttpResponseRedirect(reverse("user:show_topics", args=(username,)))

    return render(request, template_file, {"user_info": user_info})


@login_required(login_url="/home/login/")
def collect(request, username):
    from views_topic import wrap_topics_treetable
    template_file = "iUser/collect.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']

    if request.method == "POST":
        # 读取文件
        ff = FileForm(request.POST, request.FILES)
        if ff.is_valid():
            file = request.FILES.get('bookmark')
            data = file.read()
            book_marks_info = parse_bookmark(data)
            user_url_api.load_bookmark_tree(book_marks_info, username)
            return HttpResponseRedirect(reverse("user:show_topics", args=(username,)))

    return render(request, template_file, {"user_info": user_info})


def suggest(request):
    template_file = "iUser/suggest.html"
    user_info = {}
    if request.user.is_authenticated():
        username = request.user.username
        user_info = user_info_api.get_info(username)
    return render(request, template_file, {"user_info": user_info})


@login_required(login_url="/home/login/")
def add_url(request, username):
    template_file = "iUser/add_url.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']

    method = request.method
    if method == 'POST':
        url = get_request_field(request, "url", must=True)
        name = get_request_field(request, "name", must=False, default="")
        score = get_request_field(request, "score", must=False, default=50)
        topic_id = get_request_field(request, "topic_id", must=False, default=None)
        tags = get_request_field(request, "tags", must=False, default="")

        score = int(score)
        obj_info = user_url_api.add(url, username=user_info['username'],
                                    tags=tags, topic_id=topic_id, score=score, name=name)
        obj_id = obj_info['id']
        topic_id = obj_info['topic_id']
        topic_path = topic_api.get_topic_path(username, topic_id)
        base_topic = topic_path[-2]
        base_id = base_topic['child_id']
        url = reverse("user:show_topic", args=(username, topic_id))
        return HttpResponseRedirect(url)
    #
    from views_topic import wrap_as_select
    topic_root_id = topic_api.get_root_id(username)
    site_id = topic_api.get_site_id(username)
    user_topic_tree = topic_api.get_children_tree(username, topic_root_id)
    user_topic_select = wrap_as_select(user_topic_tree, target_id=site_id, level=0)
    user_topic_select = ''.join(user_topic_select)
    return render(request, template_file, {"user_info": user_info, "user_topics":user_topic_select})


@login_required(login_url="/home/login/")
def update_url(request, username, user_url_id):
    template_file = "iUser/update_user_url.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']
    user_url_info = user_url_api.get(user_url_id)

    next = get_request_field(request, "next", must=False, default="")

    method = request.method
    if method == 'POST':
        url = get_request_field(request, "url", must=True)
        name = get_request_field(request, "name", must=False, default="")
        score = get_request_field(request, "score", must=False, default=50)
        topic_id = get_request_field(request, "topic_id", must=False, default=topic_api.get_trash_id(username))
        tags = get_request_field(request, "tags", must=False, default="")

        score = int(score)
        obj_info = user_url_api.update_user_url(username, user_url_id, url=url, name=name,
                                                tags=tags, topic_id=topic_id, score=score)
        if not next:
            next = reverse("user:show_topic", args=(username, topic_id))
        return HttpResponseRedirect(next)
    #
    from views_topic import wrap_as_select
    topic_id = user_url_info["topic_id"]
    topic_root_id = topic_api.get_root_id(username)
    user_topic_tree = topic_api.get_children_tree(username, topic_root_id)
    user_topic_select = wrap_as_select(user_topic_tree, target_id=topic_id, level=0)
    user_topic_select = ''.join(user_topic_select)

    tags = ','.join([t['tag_info']['name'] for t in user_url_info['tags']])
    return render(request, template_file, {"user_url_info": user_url_info, "user_info": user_info,
                                           "tags": tags, "next": next, "user_topics": user_topic_select})


@login_required(login_url="/home/login/")
def delete_url(request, username, user_url_id):
    user_info = user_info_api.get_info(username)
    username = user_info['username']
    user_url_info = user_url_api.get(user_url_id)

    user_url_api.delete_user_url(user_url_id, username)
    next = get_request_field(request, "next", must=False, default="")
    if not next:
        next = reverse("user:show_topic", args=(username, user_url_info['topic_id']))
    return HttpResponseRedirect(next)


# @login_required(login_url="/home/login/")
# def delete_url(request, user_url_id):
#     template_file = "iUser/update_user_url.html"
#     user_info = get_user_info(request)
#     username = user_info['username']
#     user_url_info = user_url_api.get(user_url_id)
#
#     method = request.method
#     if method == 'POST':
#         url = get_request_field(request, "url", must=True)
#         name = get_request_field(request, "name", must=False, default="")
#         score = get_request_field(request, "score", must=False, default=50)
#         topic_id = get_request_field(request, "topic_id", must=False, default=None)
#         tags = get_request_field(request, "tags", must=False, default="")
#
#         score = int(score)
#         obj_info = user_url_api.update_user_url(username, user_url_id, url=url, name=name,
#                                                 tags=tags, topic_id=topic_id, score=score)
#         return HttpResponseRedirect(reverse("home:home"))
#     #
#     catenames = topic_api.get_cates(username)
#     catenames = [t['catename'] for t in catenames]
#     tags = ','.join([t['tag_info']['name'] for t in user_url_info['tags']])
#     return render(request, template_file, {"user_url_info": user_url_info, "catenames": catenames, "tags": tags})


# 各主题部分 快速移动和复制
def move_user_url(request, user_url_id):
    template_file = "iUser/move_user_url.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']
    user_url_info = user_url_api.get(user_url_id)

    next = get_request_field(request, "next", must=False, default="")

    method = request.method
    if method == "POST":
        username = user_info['username']
        user_url_id = get_request_field(request, "user_url_id", must=True)
        # catename = get_request_field(request, "catename", must=False, default="")
        topic_id = get_request_field(request, "topic_id", must=False, default=topic_api.get_trash_id(username))
        # duplicated catename, topic_id, url_id. TODO
        user_url_info = user_url_api.update_user_url(username, user_url_id, topic_id=topic_id)
        if not next:
            next = reverse("home:show_user_cate")+"?topic_id="+topic_id
        return HttpResponseRedirect(next)

    cates_info = topic_api.get_cates(username)
    topic_id = user_url_info["topic_id"]
    topics_path = topic_api.get_topic_path(username, topic_id)
    topic_base = topics_path[-2]

    return render(request, template_file, {"user_url_info": user_url_info, "topic_base": topic_base,
                                           "cates_info": cates_info, "user_url_id": user_url_id, "next": next})


# 各主题部分 快速移动和复制
def copy_user_url(request, user_url_id):
    template_file = "iUser/copy_user_url.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']
    user_url_info = user_url_api.get(user_url_id)

    next = get_request_field(request, "next", must=False, default="")
    method = request.method
    msg = ""
    if method == "POST":
        username = user_info['username']
        user_url_id = get_request_field(request, "user_url_id", must=True)
        topic_id = get_request_field(request, "topic_id", must=True)
        topic_id = int(topic_id)
        if topic_id == topic_api.get_trash_id(username):
            msg = "不能复制到垃圾桶"
        elif (topic_id == user_url_info['topic_id']):
            msg = "不能移动到同一个分类"
        else:
            url = user_url_info["url_info"]['url']
            name = user_url_info['name']
            tags = ",".join([t["tag_info"]['name'] for t in user_url_info['tags']])
            score = user_url_info['score']
            user_url_api.add(url, username=username, topic_id=topic_id, name=name, tags=tags, score=score)
            if not next:
                next = "%s?%s=%s"%(reverse("home:show_user_cate"), "topic_id", topic_id)
                print next
            return HttpResponseRedirect(next)

    cates_info = topic_api.get_cates(username)
    topic_id = user_url_info["topic_id"]
    topics_path = topic_api.get_topic_path(username, topic_id)
    topic_base = topics_path[-2]

    return render(request, template_file, {"user_url_info": user_url_info, "topic_base": topic_base,
                                           "cates_info": cates_info,
                                           "user_url_id": user_url_id, "msg": msg, "next": next})


# 用来形成首页的展示效果 -> home:home
def wrap_user_site_urls(cate_tree):
    html = []
    user_url_infos = cate_tree['user_url_infos']
    if user_url_infos:
        html.append('<li><div class="urlItems">')
        for user_url_info in user_url_infos:
            url_name = user_url_info['name']
            url = user_url_info['url_info']['url']
            tag_infos = user_url_info["user_tag_infos"]  # name, id ,type, verbose
            if not url_name: url_name = url
            html.append('<div class="urlItem">'
                        '<button type="button" class="btn btn-default" value="%s" '
                        'onclick="openItem(this.value)">%s</button></div>'%(url, url_name))
        html.append("</div></li>")

    sub_htmls = _wrap_user_site_urls(cate_tree['sub'])
    html.extend(sub_htmls)
    html = "".join(html)
    return html


def _wrap_user_site_urls(sub_topics_urls):
    html = []
    for sub_topic_url in sub_topics_urls:
        topic_name = sub_topic_url['name']
        html.append('<li><a class="panel-topic" href="">'+topic_name+'</a>')
        html.append('<ul class="submenu">')
        user_url_infos = sub_topic_url['user_url_infos']
        if user_url_infos:
            html.append('<li><div class="urlItems">')
            for user_url_info in user_url_infos:
                url_name = user_url_info['name']
                url = user_url_info['url_info']['url']
                tag_infos = user_url_info["user_tag_infos"]  # name, id ,type, verbose
                if not url_name: url_name = url
                html.append('<div class="urlItem">'
                            '<button type="button" class="btn btn-default" value="%s" '
                            'onclick="openItem(this.value)">%s</button>'
                            '</div>'%(url, url_name))
                # html.append('<div class="urlItem"><a href="%s">%s</a></div>'%(url, url_name))
            html.append("</div></li>")
        sub_sub_topics_urls = sub_topic_url['sub']
        sub_html = _wrap_user_site_urls(sub_sub_topics_urls)
        html.extend(sub_html)
        html.append("</ul>")
        html.append('</li>')
    return html



