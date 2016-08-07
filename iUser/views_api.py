# Create your views here.
#encoding:utf8

import copy
import json
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from iUserTopic.models import topic_api
from user_tools import get_user_info
from tools import get_request_field

from config import return_data


@login_required(login_url="/user/login/")
def api_get_cate_topics(request):
    # 获得一个用户下的某一个面板的所有的topics
    data = copy.copy(return_data)
    user_info = get_user_info(request)
    username = user_info['username']
    topic_id = get_request_field(request, 'topic_id', must=False, default=topic_api.get_root_id(username))
    topic_tree = topic_api.get_children_tree(username, topic_id)
    data['data'] = topic_tree
    return HttpResponse(json.dumps(data), content_type="application/json")


from get_head import get_url_title
@login_required(login_url="/user/login/")
def api_get_head(request):
    data = copy.copy(return_data)
    try:
        url = get_request_field(request, "url", must=True)
        content = get_url_title(url)
        data['data'] = content
    except Exception, ex:
        data['code'] = -1
        data['msg'] = ex.message
    return HttpResponse(json.dumps(data), content_type="application/json")


