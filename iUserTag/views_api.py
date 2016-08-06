# encoding: utf8

import copy
import json
import pdb
from django.shortcuts import render, HttpResponse

# Create your views here.

from models import Tag, TargetTag, TagHandler
from TagServerApi import TagServerApi

from Exception import wrap_exception
from tools import get_request_field
from config import return_data


from models import tag_api as tag_server_api


# @wrap_exception
# @check_auth()
def api_add_tag(request):
    data = copy.copy(return_data)
    name = get_request_field(request, "name", must=True)

    tag_info = tag_server_api.add_tag(name)
    data['data'] = tag_info
    data = json.dumps(data)
    return HttpResponse(data, content_type="application/json")


# @wrap_exception
# @check_auth()
def api_add_target(request):
    data = copy.copy(return_data)
    target_id = get_request_field(request, "target_id", must=True)
    tags_str = get_request_field(request, "tags", must=True)  # tag names seperated with comma

    # pdb.set_trace()
    tags = TagHandler.split(tags_str)
    result = tag_server_api.add_target(target_id, tags)

    data['data'] = result
    data = json.dumps(data)
    return HttpResponse(data, content_type="application/json")


# @wrap_exception
# @check_auth
def api_update_target(request):
    data = copy.copy(return_data)
    target_id = get_request_field(request, "target_id", must=True)
    tags_str = get_request_field(request, "tags", must=True)  # tag names seperated with comma

    tags = TagHandler.split(tags_str)
    result = tag_server_api.update_target_tags(target_id, tags)

    data['data'] = result
    data = json.dumps(data)
    return HttpResponse(data, content_type="application/json")


# @wrap_exception
# @check_auth
# 这个地方的target比如说是 user_url_id
def api_delete_target(request):
    data = copy.copy(return_data)
    target_id = get_request_field(request, "target_id", must=True)

    tag_server_api.delete_target(target_id)

    data = json.dumps(data)
    return HttpResponse(data, content_type="application/json")


# @wrap_exception
# @check_auth
def api_delete_target_tag(request):
    data = copy.copy(return_data)
    target_id = get_request_field(request, "target_id", must=True)
    tag_name = get_request_field(request, "tag", must=True)
    result = tag_server_api.delete_target_tag(target_id, tag_name)

    data['data'] = result
    data = json.dumps(data)
    return HttpResponse(json.dumps(data), content_type="application/json")


# @wrap_exception
# @check_auth
def api_search_target(request):
    data = copy.copy(return_data)
    target_id = get_request_field(request, "target_id", must=True)
    target_id = int(target_id)
    result = tag_server_api.search_target(target_id)

    data['data'] = result
    return HttpResponse(json.dumps(data), content_type="application/json")


# @wrap_exception
# @check_auth
def api_search_target_by_tag(request):
    data = copy.copy(return_data)
    tag_name = get_request_field(request, "name", must=True)
    target_ids = get_request_field(request, "target_ids", must=False, default="")
    target_ids = filter(lambda x: x, [t.strip() for t in target_ids.split(',')])
    target_ids = map(int, target_ids)

    result = tag_server_api.search_tag(tag_name, target_ids)

    data['data'] = result
    data = json.dumps(data)
    return HttpResponse(data, content_type="application/json")


