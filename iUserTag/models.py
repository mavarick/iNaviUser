#encoding:utf8
from __future__ import unicode_literals

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.db import models

from tools import dt_format

from config import TARGET_TAG_TABLE_NAME, TAG_TABLE_NAME

# Create your models here.
MAX_TAG_NAME = 100


class TargetTag(models.Model):
    id = models.AutoField(primary_key=True)
    target_id = models.IntegerField(null=False)
    tag_id = models.IntegerField(null=False)

    score = models.IntegerField(default=50)
    verbose = models.CharField(max_length=100)

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = TARGET_TAG_TABLE_NAME

    def get_info(self):
        return dict(
            id=self.id, target_id=self.target_id, tag_id=self.tag_id, score=self.score,
            verbose=self.verbose, status=self.status,
            last_update_time=dt_format(self.last_update_time),
            created_time=dt_format(self.created_time)
        )

    def __str__(self):
        return "{0}-{0}".format(self.target_id, self.tag_id)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=MAX_TAG_NAME, unique=True, null=False)

    type = models.IntegerField(default=0)
    verbose = models.CharField(max_length=100)

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = TAG_TABLE_NAME

    def get_info(self):
        return dict(
            id=self.id, type=self.type, name=self.name,
            verbose=self.verbose, status=self.status,
            last_update_time=dt_format(self.last_update_time),
            created_time=dt_format(self.created_time)
        )

    def __str__(self):
        name = self.name.encode("utf8") if isinstance(self.name, unicode) else self.name
        return name


class TagHandler(object):
    @staticmethod
    def split(tags_str):
        # 把逗号分隔的tags分,隔为names
        tags_str = tags_str.strip()
        if not tags_str:
            return []
        tags_str = to_utf8(tags_str)
        tags_str = tags_str.replace("，", ",")
        tags = tags_str.split(",")
        tags = [t.strip() for t in tags]
        tags = filter(lambda x: x, tags)
        return tags


def to_utf8(v):
    return v.encode("utf8") if isinstance(v, unicode) else v


############
from TagServerApi import TagServerApi
tag_api = TagServerApi(TargetTag, Tag)