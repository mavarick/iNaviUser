# encoding:utf8

import copy
import json

from django.shortcuts import render, render_to_response, HttpResponse

from CategoryApi import CategoryApi
from Exception import wrap_exception
from tools import get_request_field
from models import Category
from config import return_data
# Create your views here.

category_api = CategoryApi(Category)


@wrap_exception
def api_add_cate(request):
    # 为一个用户添加一个cate
    data = copy.copy(return_data)
    username = get_request_field(request, "username", must=True)
    catename = get_request_field(request, "catename", must=True)

    result = category_api.add_cate(username, catename)
    data['data'] = result
    return HttpResponse(json.dumps(data), content_type="application/json")


@wrap_exception
def api_add_topic(request):
    # 为一个用户的一个cate添加一个节点
    data = copy.copy(return_data)
    username = get_request_field(request, "username", must=True)
    catename = get_request_field(request, "catename", must=True)
    name = get_request_field(request, "name", must=True)
    parent_id = get_request_field(request, "parent_id", must=False, default=None)
    if parent_id is None:
        unknown_info = category_api.get_favor_id(username)
        parent_id = unknown_info['id']
    result = category_api.add(username, name, parent_id)
    data['data'] = result
    return HttpResponse(json.dumps(data), content_type="application/json")


@wrap_exception
def api_update_cate(request, id):
    # 修改一个用户的一个cate的相关信息
    data = copy.copy(return_data)
    username = get_request_field(request, "username", must=True)

    new_info = {}
    name = get_request_field(request, "name", must=False, default=None)
    if name: new_info['name'] = name
    info = get_request_field(request, "info", must=False, default=None)
    if info is not None: new_info['info'] = info

    result = category_api.update(username, id, new_info)
    data['data'] = result
    return HttpResponse(json.dumps(data), content_type="application/json")






