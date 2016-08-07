# encoding:utf8

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

# Create your views here.

from models_note import user_note_api
from models import user_info_api

from utils.tools import get_request_field
from utils.pages import wrap_pages


@login_required(login_url="/user/login/")
def add_note(request, username):
    template_file = "iUser/add_note.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']

    errors = []
    if request.method == "POST":
        info = get_request_field(request, "info", must=False, default="")
        if info:
            user_note_api.add_note(username, info)
            return HttpResponseRedirect(reverse("user:show_note", args=(username,)))
        else:
            errors.append("内容不能为空")
    return render(request, template_file, {"user_info": user_info, "errors": errors})


@login_required(login_url="/user/login/")
def show_note(request, username):
    template_file = "iUser/show_note.html"
    user_info = user_info_api.get_info(username)
    username = user_info['username']

    page = get_request_field(request, "page", must=False, default=1)
    size = get_request_field(request, "size", must=False, default=10)

    page = int(page)
    size = int(size)
    notes = user_note_api.get_notes(username, page=page, size=size)
    count = user_note_api.count(username)
    page_url = reverse("user:show_note", args=(username, ))
    page_url = "{0}?page=%s&size={1}".format(page_url, size)
    page_info = wrap_pages(page_url, cnt=count, size=size, cur=page, span=10)

    return render(request, template_file, {"user_info": user_info, "notes": notes, "count": count, "page_info": page_info})

