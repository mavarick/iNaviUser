# encoding:utf8
from __future__ import unicode_literals
import os

from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import BaseUserManager
from django import forms
from utils.tools import dt_format

# from models_url import UserUrl
from config import MAX_USERNAME_LENGTH


class UserInfo(models.Model):
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, primary_key=True)
    bio = models.CharField(max_length=200, default="写上你的格言, 也许会激励很多人")

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_info"

    def get_info(self):
        data = dict(username=self.username, bio=self.bio,
                    status=self.status, last_update_time=dt_format(self.last_update_time),
                    create_time=dt_format(self.create_time))
        return data


# 这个地方指向人的职业
class UserSkill(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, null=False, blank=False)
    name = models.CharField(max_length=50, null=False, blank=False)

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_skills"

    def get_info(self):
        id = self.id
        name = self.name
        username = self.username
        return dict(id=id, username=username, name=name)


class UserInterest(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, null=False, blank=False)
    name = models.CharField(max_length=50, null=False, blank=False)

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_interest"

    def get_info(self):
        id = self.id
        username = self.username
        name = self.name
        return dict(id=id, username=username, name=name)


from upload_avatar.signals import avatar_crop_done
from upload_avatar.models import UploadAvatarMixIn


class UserAvatar(models.Model, UploadAvatarMixIn):
    # user = models.ForeignKey('auth.User', related_name='user_info')
    # user = models.ForeignKey('auth.User', related_name='user_info')
    username = models.CharField(max_length=255, primary_key=True)
    avatar_name = models.CharField(max_length=128)

    status = models.IntegerField(default=0)
    last_update_time = models.DateTimeField(null=True, blank=True, auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def get_uid(self):
        return self.username

    def get_avatar_name(self, size):
        return UploadAvatarMixIn.build_avatar_name(self, self.avatar_name, size)


def save_avatar_in_db(sender, username, avatar_name, **kwargs):
    if UserAvatar.objects.filter(username=username).exists():
        UserAvatar.objects.filter(username=username).update(avatar_name=avatar_name)
    else:
        UserAvatar.objects.create(username=username, avatar_name=avatar_name)

avatar_crop_done.connect(save_avatar_in_db)


class UserInfoApi(object):

    def __init__(self, UserInfo, UserSkill, UserInterest):
        self.user_info = UserInfo
        self.user_skill = UserSkill
        self.user_interest = UserInterest

    def create_user(self, username):
        self.user_info.objects.filter(username=username).delete()
        obj = self.user_info.objects.create(username=username)
        return obj.get_info()

    def update_skill(self, username, skill_names):
        self.user_skill.objects.filter(username=username).delete()
        for skill_name in skill_names:
            self.user_skill.objects.get_or_create(username=username, name=skill_name)

    def update_interest(self, username, interest_names):
        self.user_interest.objects.filter(username=username).delete()
        for interest_name in interest_names:
            self.user_interest.objects.get_or_create(username=username, name=interest_name)

    def update_bio(self, username, new_bio):
        obj, _flag = self.user_info.objects.get_or_create(username=username)
        obj.bio = new_bio
        obj.save()
        return obj.get_info()

    def get_info(self, username):
        user_info_obj = self.user_info.objects.get(username=username)
        user_info = user_info_obj.get_info()
        user_skill_objs = self.user_skill.objects.filter(username=username)
        user_skills = [t.get_info() for t in user_skill_objs]
        user_interest_objs = self.user_interest.objects.filter(username=username)
        user_interests = [t.get_info() for t in user_interest_objs]
        try:
            user_avatar_obj = UserAvatar.objects.get(username=username)
            user_avatar_url = user_avatar_obj.get_avatar_url()
            print user_avatar_url
        except Exception, ex:
            user_avatar_url = '/static/avatar/default.jpg'

        user_info['user_skills'] = user_skills
        user_info['user_interests'] = user_interests
        user_info['user_avatar'] = user_avatar_url
        return user_info

    def update_user_info(self, username, bio=None, skills=[], interests=[]):
        if bio:
            self.update_bio(username, bio)
        if skills:
            self.update_skill(username, skills)
        if interests:
            self.update_interest(username, interests)
        return self.get_info(username)

    def drop_user(self, username):
        User.objects.filter(username=username).delete()
        self.user_info.objects.filter(username=username).delete()
        self.user_skill.objects.filter(username=username).delete()
        self.user_interest.objects.filter(username=username).delete()

    def get_recent_users(self, size=10, page=1):
        users = self.user_info.objects.order_by("-create_time")[0:size]
        user_infos = [self.get_info(t.username) for t in users]
        return user_infos


user_info_api = UserInfoApi(UserInfo, UserSkill, UserInterest)

# class ProfileBase(type):
#     def __new__(cls, name, bases, attrs):
#         module = attrs.pop("__module__")
#         parents = [b for b in bases if isinstance(b, ProfileBase)]
#         if parents:
#             fields = []
#             for obj_name, obj in attrs.iteritems():
#                 if isinstance(obj, models.Field):
#                     fields.append(obj_name)
#                     User.add_to_class(obj_name, obj)
#             UserAdmin.fieldsets = list(UserAdmin.fieldsets)
#             UserAdmin.fieldsets.append((name, {"fields": fields}))
#         return super(ProfileBase, cls).__new__(cls, name, bases, attrs)
#
#
# class Profile(object):
#     __metaclass__ = ProfileBase
#
#
# class iUserManager(BaseUserManager):
#
#     def create_user(self, username, email, password=None, **kargs):
#         if not email:
#             raise ValueError("Users must have an email address")
#         user = self.model(username=username, email=BaseUserManager.normalize_email(email), **kargs)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, username, email, password=None, **kargs):
#         user = self.create_user(username, email, password, **kargs)
#         user.is_admin = True
#         user.save(using=self._db)
#         return user


'''
User has fields below: username, email, add_time, update_time, is_delete, is_active, is_admin
So if other fields are wanted, add them here!!
'''

#
# class MyProfile(Profile):
#     # add other fields here!
#     #add_time = models.DateTimeField(blank=True, null=True)
#     pass


class UserForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='password conformation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']



