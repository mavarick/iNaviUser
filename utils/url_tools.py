#!/usr/bin/env python
# encoding:utf8

# 获取一个网址的跟网址
import urlparse
def get_url_root(url):
    '''获得地址的跟地址，注意url必须是http开头
    '''
    elem = urlparse.urlparse(url)
    scheme, netloc = elem.scheme, elem.netloc
    return "{}://{}".format(scheme, netloc)

def standize_url(url):
    if "://" not in url:
        url = "http://{}".format(url)
    # if not url.startswith("http://") and not url.startswith("https://"):  # ftp etc
    #     url = "http://{}".format(url)
    return url

