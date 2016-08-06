#!/usr/bin/env python
# encoding:utf8

# 获取一个网址的跟网址
import re
import urlparse


def get_url_root(url):
    """获得地址的跟地址，注意url必须是http开头
    """
    elem = urlparse.urlparse(url)
    scheme, netloc = elem.scheme, elem.netloc
    return "{}://{}".format(scheme, netloc)


def std_url(url):
    if "://" not in url:
        url = "http://{}".format(url)
    # if not url.startswith("http://") and not url.startswith("https://"):  # ftp etc
    #     url = "http://{}".format(url)
    return url


re_site = r"https?://[^.]+\."
def format_site(url):
    # 去掉相关的参数
    # 检查是否可用
    elem = urlparse.urlparse(url)
    scheme, netloc, path = elem.scheme, elem.netloc, elem.path
    site = "{0}://{1}{2}".format(scheme, netloc, path)
    if not site.endswith('/'):
        site = "{0}/".format(site)
    return site


def quote_url(url):
    # TODO
    pass