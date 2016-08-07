from __future__ import unicode_literals

from django.db import models
from utils.tools import dt_format

# Create your models here.
table_name = "user_note"
MAX_USERNAME_LENGTH = 200


class UserNote(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, null=False, default="", db_column="username")
    info = models.TextField(null=False, blank=False)

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = table_name

    def __str__(self):
        return self.url

    def get_info(self):
        return dict(id=self.id, username=self.username,
                    info=self.info, status=self.status,
                    last_update_time=dt_format(self.last_update_time),
                    created_time=dt_format(self.created_time))


class UserNoteApi(object):
    def __init__(self, UserNote):
        self.model = UserNote

    def add_note(self, username, info):
        if not username or not info:
            raise Exception("You must login and type something")
        obj = self.model.objects.create(username=username, info=info)

    def get_notes(self, username=None, page=1, size=10):
        if not page: page = 1
        if not size: size = 10
        st, et = (page-1)*size, page*size
        if username:
            objs = self.model.objects.filter(username=username).order_by("-created_time")[st:et]
        else:
            objs = self.model.objects.order_by("-created_time")[st:et]
        return [t.get_info() for t in objs]

    def count(self, username=None):
        if username:
            return self.model.objects.filter(username=username).count()
        else:
            return self.model.objects.count()

user_note_api = UserNoteApi(UserNote)
