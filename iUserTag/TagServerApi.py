# encoding:utf8
import pdb


class TagServerApi(object):
    """ 功能: 对 target 的tags 的CRUD操作
    两个部分: target_tag 部分和 tag部分

    注意: tag 是没有任何的
    """
    def __init__(self, rel_model, tag_model):
        """ 包含两种表: 关联表, 和 节点表
        :param rel_table: 关联表, target_id:int, tag_id:int
        :param tag_table: tag表, tag_id:int, name: char
        """
        self.rel_model = rel_model
        self.tag_model = tag_model

    def add_tag(self, tag_name, tag_info={}):
        tag_name = tag_name.strip()
        if not tag_name:
            raise Exception("tag name: [{}] is empty".format(tag_name))
        obj, created = self.tag_model.objects.get_or_create(name=tag_name, defaults=tag_info)
        return obj.get_info()

    def add_target_tag(self, target_id, tag_name, tag_info={}):
        tag_obj = self.add_tag(tag_name, tag_info=tag_info)
        tag_id = tag_obj['id']
        target_obj, created = self.rel_model.objects.get_or_create(target_id=target_id,
                tag_id=tag_id, defaults=tag_info)
        target_tag_info = target_obj.get_info()
        target_tag_info['tag_info'] = tag_obj
        return target_tag_info

    def add_target(self, target_id, tag_name_list):
        result = []
        for name in tag_name_list:
            item = self.add_target_tag(target_id, name)
            result.append(item)
        return result

    def update_target_tags(self, target_id, tag_name_list):
        # delete the total tags
        self.rel_model.objects.filter(target_id=target_id).delete()
        result = self.add_target_tags(target_id, tag_name_list)
        return result

    def search_target(self, target_id):
        # 2.1.4 查询target所对应的所有的tags
        targets = self.rel_model.objects.filter(target_id=target_id)
        result = []
        for t in targets:
            tag_id = t.tag_id
            target_info = t.get_info()
            tag_obj = self.tag_model.objects.get(pk=tag_id)
            tag_info = tag_obj.get_info()
            target_info['tag_info'] = tag_info
            result.append(target_info)
        return result

    def search_tag(self, tag_name, target_ids_choices=[]):
        # 2.1.5 反差,根据tagid查询所对应的targetids
        # target_id_choices指的是target_ids的scopes. 比如从一个用户的数据中抽取同样标签的链接数据
        tag_info = dict(name=tag_name)
        obj, created = self.tag_model.objects.get_or_create(name=tag_name, defaults=tag_info)
        if created:
            return []
        tag_id = obj.id
        targets = self.rel_model.objects.filter(tag_id=tag_id)
        if target_ids_choices:
            targets = targets.filter(target_id__in=target_ids_choices)
        return [t.target_id for t in targets]

    def delete_target(self, target_id):
        self.rel_model.objects.filter(target_id=target_id).delete()

    def delete_target_tag(self, target_id, tag_name):
        obj, created = self.tag_model.objects.get_or_create(name=tag_name)
        tag_id = obj.id
        targets = self.rel_model.objects.filter(target_id=target_id, tag_id=tag_id)
        cnt = 0
        for obj in targets:
            obj.delete()
            cnt += 1
        data = {"count": cnt}
        return data







