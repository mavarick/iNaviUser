# encoding:utf8


class TagHandler(object):
    @staticmethod
    def split(tags_str):
        # 把逗号分隔的tags分,隔为names
        tags_str = tags_str.strip()
        if not tags_str:
            return []
        tags_str = to_utf8(tags_str)
        tags_str = tags_str.replace("，", ",")
        tags = tags_str.split(",")
        tags = [t.strip() for t in tags]
        tags = filter(lambda x: x, tags)
        return tags


def to_utf8(v):
    return v.encode("utf8") if isinstance(v, unicode) else v

