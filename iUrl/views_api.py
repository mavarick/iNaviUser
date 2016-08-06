#encoding:utf8

import copy
import json
from django.shortcuts import render, HttpResponse

# Create your views here.
from models import URL, UrlApi
from auth import check_auth
from Exception import wrap_exception
from tools import get_request_field
from config import return_data


url_api = UrlApi(URL)


@wrap_exception
@check_auth
def api_add(request):
    data = copy.copy(return_data)
    url = get_request_field(request, "url", must=True)
    username = get_request_field(request, "username", must=False, default="")
    url_info = url_api.add(dict(url=url, username=username))

    data['data'] = url_info
    data = json.dumps(data)

    return HttpResponse(data, content_type="application/json")


