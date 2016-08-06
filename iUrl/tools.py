#!/usr/bin/env python
# encoding:utf8

import datetime
import time
import hashlib


def dt_format(dt, format="%Y-%m-%d %H:%M:%S"):
    if not dt: return str(dt)
    return dt.strftime(format)


def test_dt_format():
    now = datetime.datetime.now()
    print dt_format(now)


def ts2time(timestamp, format="%Y-%m-%d %H:%M:%S"):
    t = time.gmtime(timestamp)
    return time.strftime(format, t)


# 获得请求的request相关信息
def get_request_info(req):
    meta = req.META
    client_ip = meta.get("REMOTE_ADDR", "U")
    data = dict(client_ip=client_ip)
    return data


def get_request_field_by_method(request, field_name, method='POST', must=False, default=None):
    ''' get field value from request dict,

    :param request: request.
    :param field_name: field name.
    :param method: POST, GET, REQUEST
    :param must: if true, must be not None.
    :param default: if missing, then should be this value
    :return: field value
    '''
    request_dict = getattr(request, method)
    if must:
        field_value = request_dict[field_name]
    else:
        field_value = request_dict.get(field_name, default)
    return to_utf8(field_value)


def get_request_field(request, field_name, must=False, default=None):
    # use post or get method to get request fields values
    field_value = get_request_field_by_method(request, field_name, method='GET', must=False, default=None)
    if field_value is not None:
        return field_value
    field_value = get_request_field_by_method(request, field_name, method='POST', must=must, default=default)
    return field_value


# 获得request中对应的field_name的信息，如果不是post，那么进行get测试
def get_field(request, field_name):
    return request.REQUEST.get(field_name, None)


def get_hash_id(str):
    return hashlib.md5(str).hexdigest()


def to_utf8(s):
    if isinstance(s, unicode):
        s = s.encode("utf8")
    return s


if __name__ == "__main__":
    test_dt_format()

