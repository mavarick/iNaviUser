# encoding: utf8
import math


def wrap_pages(path, cnt, size, cur, span=10):
    """ generate the pagination items
    :param path: "path?page=%s&size=size"
    :param size: size
    :param cur:  current page number
    :param cnt:  total item cnt
    :param span: number of page tags, as 3: 1,2,3, [(first, 1,2,3,..., 100)]
    :return: list for pagination as [(name, url), (name, )]
    """
    tags = []
    max_page = int(math.ceil(cnt*1.0/size))
    sp, ep = cur - span/2, cur + span/2
    offset = 0
    if sp < 1:
        offset = 1 - sp
        sp = 1
    ep += offset - 1
    if ep > max_page: ep = max_page
    pages = range(sp, ep+1)

    # add the first
    cur_flag = 0
    if not pages or pages[0] != 1:
        tags.append(("1", path%1, cur_flag))
    if len(pages) > 1 and pages[1] != 2:
        tags.append(("...", "", 1))
    for page in pages:
        cur_flag = 0
        if page == cur:
            cur_flag = 1
        tags.append((page, path%page, cur_flag))
    # add the end
    cur_flag = 0

    if pages and pages[-1] != max_page:
        if pages[-1] + 1 != max_page:
            tags.append(('...', "", 1))
        tags.append((max_page, path%max_page, cur_flag))
    tags.append(("共%s条"%cnt, "", 1))
    return tags
