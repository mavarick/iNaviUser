from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.
from iUser.models import user_info_api
from iUser.models_url import user_url_api


def login(request):
    return HttpResponseRedirect(reverse("user:login"))


def register(request):
    return HttpResponseRedirect(reverse("user:register"))


def get_index(request):
    tempalte_file = "index/index.html"

    user_info = {}
    if request.user.is_authenticated():
        username = request.user.username
        user_info = user_info_api.get_info(username)
    recent_urls = user_url_api.get_recent_urls(size=10)
    recent_users = user_info_api.get_recent_users(size=10)
    return render(request, tempalte_file, {"user_info": user_info,
        "users": recent_users, "urls": recent_urls})





