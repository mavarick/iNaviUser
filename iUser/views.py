# encoding:utf8
# Create your views here.
import os

from django.shortcuts import render, render_to_response, get_object_or_404, RequestContext
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
from models_url import user_url_api
from utils.pages import wrap_pages

def register(request):
    cur_time = timezone.now()
    register_template = "iUser/register.html"

    if request.user.is_authenticated():
        jump_template = "iUser/jump.html"
        return render(request, jump_template, {"msg": "You have already login!"})

    # user_form = UserForm(instance=User())
    errors = []
    if request.method == "POST":
        username = request.POST.get('username', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get("password2", '')
        email = request.POST.get("email", "")

        # user_form.username = username
        # user_form.password1 = password1
        # user_form.password2 = password2
        # user_form.email = email

        if password1 != password2:
            errors.append("password are not matched")
            return render_to_response(register_template,
                {'errors': errors})
        password = password1

        is_username_exist = User.objects.filter(username=username)
        if len(is_username_exist) > 0:
            errors.append("User already exists")
            return render(request, register_template, {'errors': errors})
        # create user
        User.objects.create_user(username=username, password=password, email=email)
        # init environment
        init_env(username)
        # authenticate user
        # user = auth.authenticate(username=username, password=password)

        return HttpResponseRedirect(reverse("user:login"))
    else:
        return render(request, register_template, {"errors": errors})


def init_env(username):
    user_info_api.create_user(username)
    topic_api.init(username)


def login(request):
    login_template = "iUser/login.html"
    errors = []
    if request.user.is_authenticated():
        jump_template = "iUser/jump.html"
        return render(request, jump_template, {"msg": "You have already login!"})
    # lazy way to avoid inputting username and password each time
    # username = request.COOKIES.get('username', '')
    # password = request.COOKIES.get('password', '')
    # user = auth.authenticate(username=username, password=password)
    # if user and user.is_active:
    #     auth.login(request, user)
    #     return HttpResponseRedirect(reverse("iUser:home"))
    ###############

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            response = HttpResponseRedirect(reverse("user:main", args=(username,)))
            response.set_cookie("username", username)
            return response

        errors.append("Username and password doesn't match")
    return render(request, login_template, {"form": request.POST, "errors": errors})


def logout(request):
    logout_template = "iUser/jump.html"
    if request.user.is_authenticated():
        auth.logout(request)
    next_page = {"url": reverse("index:index"), "name":"主页"}
    response = render(request, logout_template, {"next": next_page, "msg":"成功退出"})
    response.delete_cookie('username', path='/')
    # response.delete_cookie('password', path='/')
    return response


def page_info(request, username):
    template_file = "iUser/user_info.html"
    user_info = user_info_api.get_info(username)
    return render(request, template_file, {"user_info": user_info, "id": id})


def drop_user(request, username):
    jump_template = "iUser/jump.html"
    msg = ""
    # username = request.GET.get("username", "")
    user_obj = get_object_or_404(User, username=username)
    user_info_api.drop_user(username)
    topic_api.delete_user(username)

    next_page = {"url": reverse("index:index"), "name":"主页"}
    response = render(request, jump_template, {"next": next_page, "msg":msg})
    return response


from user_tools import get_user_info
# 登录用户的首页视图, 包含了导航\收藏等信息,不是index
def main(request, username):
    auth = False
    if request.user.is_authenticated():
        user_info = get_user_info(request)
        login_username = user_info['username']
        if login_username == username:
            auth = True
    if not auth:
        # 输出用户信息
        return HttpResponseRedirect(reverse("user:info", args=(username,)))

    site_id = topic_api.get_site_id(username)
    site_tree = user_url_api.get_topic_total_info(username, site_id)
    user_info = user_info_api.get_info(username)

    # 最近收藏
    user_recent_urls = user_url_api.get_recent_urls(username, size=10, page=1)
    template_file = "iUser/index.html"

    return render(request, template_file, {"user_info": user_info, "id": id,
                                           "site_tree": site_tree, "user_recent_urls":user_recent_urls})


# def update_figure(request, username):
#     if not request.user.is_authenticated():
#         return HttpResponseRedirect(reverse("user:login"))
#
#     user = request.user
#     username = user.username
#     if request.method == "POST":
#         new_bio = request.POST.get("bio", "")
#         user_info_api.update_bio(username, new_bio)
#         return HttpResponseRedirect(reverse("user:info", args=(username, )))
#     template_file = "iUser/update_figure.html"
#     user_info = user_info_api.get_info(username)
#     return render(request, template_file, {"user_info": user_info})


def update_bio(request, username):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("user:login"))

    user = request.user
    username = user.username
    if request.method == "POST":
        new_bio = request.POST.get("bio", "")
        user_info_api.update_bio(username, new_bio)
        return HttpResponseRedirect(reverse("user:info", args=(username, )))
    template_file = "iUser/update_bio.html"
    user_info = user_info_api.get_info(username)
    return render(request, template_file, {"user_info": user_info})


def update_skills(request, username):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("user:login"))

    user = request.user
    username = user.username
    if request.method == "POST":
        new_skills_str = request.POST.get("skills", "")
        new_skills = TagHandler.split(new_skills_str)
        user_info_api.update_skill(username, new_skills)
        return HttpResponseRedirect(reverse("user:info", args=(username, )))
    template_file = "iUser/update_skills.html"
    user_info = user_info_api.get_info(username)
    skills = ','.join([t['name'] for t in user_info['user_skills']])
    return render(request, template_file, {"user_info": user_info, "skills": skills})


def update_interests(request, username):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("user:login"))

    user = request.user
    username = user.username
    if request.method == "POST":
        new_insterest_str = request.POST.get("interests", "")
        new_insterests = TagHandler.split(new_insterest_str)
        user_info_api.update_interest(username, new_insterests)
        return HttpResponseRedirect(reverse("user:info", args=(username, )))
    template_file = "iUser/update_interests.html"
    user_info = user_info_api.get_info(username)
    interests = ','.join([t['name'] for t in user_info['user_interests']])
    return render(request, template_file, {"user_info": user_info, "interests": interests})


from upload_avatar.app_settings import (
    UPLOAD_AVATAR_UPLOAD_ROOT,
    UPLOAD_AVATAR_AVATAR_ROOT,
    UPLOAD_AVATAR_RESIZE_SIZE,
)


from upload_avatar import get_uploadavatar_context
from .models import UserAvatar


#########################
# In production, you don't need this,
# static files should serve by web server, e.g. Nginx

def find_mimetype(filename):
    """In production, you don't need this,
    Static files should serve by web server, e.g. Nginx.
    """
    if filename.endswith(('.jpg', '.jpep')):
        return 'image/jpeg'
    if filename.endswith('.png'):
        return 'image/png'
    if filename.endswith('.gif'):
        return 'image/gif'
    return 'application/octet-stream'


def get_upload_images(request, filename):
    mimetype = find_mimetype(filename)
    with open(os.path.join(UPLOAD_AVATAR_UPLOAD_ROOT, filename), 'r') as f:
        #return HttpResponse(f.read(), mimetype=mimetype)
        return HttpResponse(f.read(), content_type=mimetype)


def get_avatar(request, filename):
    mimetype = find_mimetype(filename)
    with open(os.path.join(UPLOAD_AVATAR_AVATAR_ROOT, filename), 'r') as f:
        #return HttpResponse(f.read(), mimetype=mimetype)
        return HttpResponse(f.read(), content_type=mimetype)

# print "got here 11111>>>>>>>>>>>>>>>"
@login_required(login_url="/user/login/")
def update_figure(request, username):
    return render_to_response(
        'iUser/upload_avatar.html',
        get_uploadavatar_context(),
        context_instance=RequestContext(request)
    )


