#!/usr/bin/env python
# encoding:utf8

import copy
import json

from django.shortcuts import HttpResponse

from config import return_data
from tools import get_request_field

from config import return_data, AUTH_CODE


def check_auth(auth=AUTH_CODE):
    def wrap_outer(func):
        def wrap_inner(request, *args, **kwargs):
            _auth = get_request_field(request, 'auth', must=False, default="")
            if _auth == auth:
                return func(request, *args, **kwargs)
            else:
                data = copy.deepcopy(return_data)
                data['code'] = -10
                data['msg'] = "wrong auth code"
                data = json.dumps(data)
                return HttpResponse(data, content_type="application/json")
        return wrap_inner
    return wrap_outer


def test():
    class req:
        def __init__(self):
            self.POST = {"auth": 111}
            self.GET = {"auth": 111}
    @check_auth()
    def foo(r):
        print "inner foo"

    print foo(req())

if __name__ == "__main__":
    test()
