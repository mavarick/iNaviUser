# encoding:utf8
from __future__ import unicode_literals

from django.db import models
from tools import dt_format, get_hash_id
from url_tools import std_url

# Create your models here.
USERNAME_MAX_LENGTH = 100


class URL(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    url = models.TextField(null=False)

    title = models.CharField(max_length=255, null=False, blank=True)
    abstract = models.TextField(null=False, blank=True)
    info = models.TextField(null=False, blank=True)

    username = models.CharField(max_length=USERNAME_MAX_LENGTH, null=False, default="", db_column="username")
    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "url"

    def __str__(self):
        return self.url

    def get_info(self):
        return dict(id=self.id, url=self.url, username=self.username,
                    title=self.title, abstract=self.abstract, info=self.info,
                    status=self.status,
                    last_update_time=dt_format(self.last_update_time),
                    created_time=dt_format(self.created_time))


class UrlApi(object):
    def __init__(self, url_model):
        self.model = url_model

    def add(self, data_dict):
        url = data_dict['url']
        if not url:
            raise Exception("url is empty")
        url = std_url(url)
        username = data_dict.get("username", "")
        status = data_dict.get("status", 50)

        url_id = get_hash_id(url)
        data_dict = dict(id=url_id, url=url, username=username, status=status)
        obj, created = self.model.objects.get_or_create(id=url_id, defaults=data_dict)
        return obj.get_info()

    def get(self, url_id):
        obj = self.model.objects.get(pk=url_id)
        return obj.get_info()


url_api = UrlApi(URL)
