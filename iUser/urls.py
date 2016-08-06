# encoding: utf8
"""iNaviUser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from views import main, login, register, logout, page_info, drop_user, update_bio, update_skills, update_interests

from views_topic import show_topic, show_topics, update_topic, delete_topic, add_topic
from views_api import api_get_cate_topics, api_get_head
from views_url import add_url, show_urls, update_url, delete_url, upload_bookmark, collect, suggest

urlpatterns = [
    url(r'^login/?$', login, name="login"),
    url(r'^register/?$', register, name="register"),
    url(r'^logout/?$', logout, name="logout"),
    url(r'^suggest/?$', suggest, name="suggest"),
    url(r'^(?P<username>\w+)/?$', main, name="main"),
    url(r'^(?P<username>\w+)/info/?$', page_info, name="info"),
    url(r'^(?P<username>\w+)/delete/?$', drop_user, name="delete"),
    url(r'^(?P<username>\w+)/update_bio/?$', update_bio, name="update_bio"),
    url(r'^(?P<username>\w+)/update_skills/?$', update_skills, name="update_skills"),
    url(r'^(?P<username>\w+)/update_interests/?$', update_interests, name="update_interests"),

    url(r'^(?P<username>\w+)/topic/(?P<topic_id>\d+)/?$', show_topic, name="show_topic"),
    # 这个地方用 show_topics 来跳转,防止每次都要取出用户的root_id
    url(r'^(?P<username>\w+)/topics/?$', show_topics, name="show_topics"),
    url(r'^(?P<username>\w+)/add_topic/?$', add_topic, name="add_topic"),
    url(r'^(?P<username>\w+)/update_topic/(?P<topic_id>\d+)/?$', update_topic, name="update_topic"),
    url(r'^(?P<username>\w+)/delete_topic/(?P<topic_id>\d+)/?$', delete_topic, name="delete_topic"),

    # urls
    url(r'^(?P<username>\w+)/add_url/?$', add_url, name="add_url"),
    url(r'^(?P<username>\w+)/update_url/(?P<user_url_id>\d+)/?$', update_url, name="update_url"),
    url(r'^(?P<username>\w+)/delete_url/(?P<user_url_id>\d+)/?$', delete_url, name="delete_url"),
    url(r'^(?P<username>\w+)/latest/?$', show_urls, name="latest"),
    url(r'^(?P<username>\w+)/bookmark/?$', upload_bookmark, name="upload_bookmark"),
    url(r'^(?P<username>\w+)/collect/?$', collect, name="collect"),


    # apis
    url(r"api/get_cate_topics/?", api_get_cate_topics, name="get_cate_topics"),
    url(r"api/api_get_head/?", api_get_head, name="api_get_head")
]
