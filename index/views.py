from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.
from iUser.models import user_info_api
from iUser.models_url import user_url_api
from utils.tools import get_request_field
from utils.pages import wrap_pages


def login(request):
    return HttpResponseRedirect(reverse("user:login"))


def register(request):
    return HttpResponseRedirect(reverse("user:register"))


def get_index(request):
    tempalte_file = "index/index.html"

    user_info = {}
    username = None
    if request.user.is_authenticated():
        username = request.user.username
        user_info = user_info_api.get_info(username)
        username = user_info['username']
    page = get_request_field(request, "page", must=False, default=1)
    size = get_request_field(request, "size", must=False, default=10)
    page = int(page)
    size = int(size)

    page_url = reverse("index:index")
    page_url = "{0}?page=%s&size={1}".format(page_url, size)
    recent_urls = user_url_api.get_urls(username=username, size=size, page=page)
    cnt = user_url_api.get_urls_count()
    page_info = wrap_pages(page_url, cnt=cnt, size=size, cur=page, span=10)

    recent_users = user_info_api.get_recent_users(size=10)
    return render(request, tempalte_file, {"user_info": user_info,
        "users": recent_users, "urls": recent_urls, "count": cnt, "page_info": page_info})





