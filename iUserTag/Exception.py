# encoding:utf8

import copy
import json
import traceback

from django.shortcuts import HttpResponse

from config import return_data


def wrap_exception(func):
    def wrapper(request, *args, **kwargs):
        data = copy.deepcopy(return_data)
        try:
            return func(request, *args, **kwargs)
        except Exception, ex:
            data["code"] = -1
            data['msg'] = ex.message
            data['data'] = traceback.format_exc()
        return HttpResponse(json.dumps(data), content_type="application/json")
    return wrapper

