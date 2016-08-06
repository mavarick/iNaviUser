# encoding:utf8
# 主要用来操作bookmark的数据

import time
import pdb

from bs4 import BeautifulSoup as BS
from bs4.element import Tag

# firefox
def parse_bookmark(content):
    # 对书签进行处理, 补充DT和DD, 来保证BS解析的时候不会出现问题
    new_content = clean(content)

    bs = BS(new_content)
    contents = bs.body.dl.contents
    # pdb.set_trace()
    info = dict(name="导入的书签")
    info = _parse_bookmark(contents, info)
    return info


def _parse_bookmark(contents, info={}):
    # contents should be list of dt/dd/dl etc
    url_infos = []
    topic_infos = []
    index = 0
    sub_topic_flag = 0
    while index < (len(contents)):
        content = contents[index]
        if not isinstance(content, Tag):
            index += 1
            continue
        if content.name == 'dt':
            # 查看是否是有效的a
            href = content.find('a')
            if href:
                # 说明是link
                sub_topic_flag = 0
                link = parse_href(href)
                url_infos.append(link)
            else:
                h3 = content.find("h3")
                if h3:
                    sub_topic_flag = 1
                    topic_info = parse_topic_name(h3)
            # 查看后面是否是dd
        if content.name == 'dd':
            if url_infos:
                url_infos[-1]['info'] = content.text
        if content.name =="dl":
            if sub_topic_flag == 1 and topic_info: # 说明前面有topic
                topic_info = _parse_bookmark(content.contents, topic_info)
                topic_infos.append(topic_info)
                sub_topic_flag = 0
        index += 1
    info['url_infos'] = url_infos
    info['sub'] = topic_infos
    return info


def parse_href(a_element):
    url = a_element['href']
    name = a_element.text
    created_time = tran_ts2time(a_element['add_date'])
    last_update_time = tran_ts2time(a_element['last_modified'])
    return dict(url=url, name=name, created_time=created_time, last_update_time=last_update_time)


def parse_topic_name(h3_element):
    name = h3_element.text
    created_time = tran_ts2time(h3_element['add_date'])
    last_update_time = tran_ts2time(h3_element['last_modified'])
    return dict(name=name, created_time=created_time, last_update_time=last_update_time)


def tran_ts2time(ts):
    ts = int(ts)
    t = time.localtime(ts)
    return time.strftime('%Y-%m-%d %H:%M:%S', t)


def clean(content):
    # 如果是DT开头,就在后面加</DT>, DD同理
    new_content = []
    for line in content.split('\n'):
        line_strip = line.strip()
        if line_strip.startswith("<DT>"):
            new_line = line.strip("\r\n")+"</DT>"
        elif line_strip.startswith("<DD>"):
            new_line = line.strip("\r\n")+"</DD>"
        else:
            new_line = line
        new_content.append(new_line)
    return ''.join(new_content)


def test():
    filename = "bookmarks.html"
    content = open(filename).read()
    info = parse_bookmark(content)
    print info


if __name__ == "__main__":
    test()



