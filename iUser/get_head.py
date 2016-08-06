# encoding:utf8
# 获得网页的head信息

import pdb
import urllib
import requests
import json
from utils.url_tools import standize_url

AUTH_CODE = ""
opener = "http://localhost:8010/open/header/?url=%s&auth=%s&by=r"
opener_alexa = "http://localhost:8010/open/alexa/?url=%s&by=r&auth=%s"


def get_alexa_site_name(url):
    url_quote = urllib.quote(url)
    site_name = ""
    try:
        url = opener_alexa%(url_quote, AUTH_CODE)
        data = requests.get(url)
        content = data.content
        data = json.loads(content)
        data = data['data']
        site_name = data['info']['site_name']
        site_name = site_name.strip('-')
    except Exception, ex:
        pass
    return site_name


def get_site_title(url):
    url_quote = urllib.quote(url)
    url = opener%(url_quote, AUTH_CODE)
    title = ""
    try:
        data = requests.get(url)
        content = data.content
        data = json.loads(content)
        data = data['data']
        title = data['title']
    except Exception, ex:
        pass
    return title


def get_url_title(url):
    url = standize_url(url)
    title = get_alexa_site_name(url)
    if not title:
        title = get_site_title(url)
    return title


def test():
    url = "http://www.baidu.com"
    print get_url_title(url)


if __name__ == "__main__":
    test()