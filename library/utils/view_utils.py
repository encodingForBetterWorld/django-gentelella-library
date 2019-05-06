# coding=utf-8
from __builtin__ import unicode

from django.db.models import Func, CharField
from copy import copy
from datetime import datetime, timedelta


def general_queryset_order(queryset, order):
    if order:
        is_asc = not order.startswith("-")
        order_field = is_asc and order or order[1:]
        if isinstance(queryset.model._meta.get_field(order_field), CharField):
            # 字符字段如果包含中文，使用中文首字母排序
            queryset = queryset.annotate(zh_gbk_order_tmp_field=Func(order_field,
                                                                     function='gbk_chinese_ci',
                                                                     template='CONVERT(%(expressions)s USING gbk) COLLATE "%(function)s"'
                                                                     ))
            order = is_asc and "zh_gbk_order_tmp_field" or "-zh_gbk_order_tmp_field"
        queryset = queryset.order_by(order).all()
    return queryset


def get_fields(data, use_choices=True, format_date=True, default_str='暂无', **ex_rules):
    """
    export fields form data
    :param data: 待转换数据
    :param use_choices: 默认使用django_model choices
    :param format_date: 默认日期格式化
    :param transform_foreign_field: 默认转换外键
    :param default_str: 默认内容
    :return:
    """
    transform_rules = getattr(data, "transform_rules", None)
    exclude_fields = getattr(data, "exclude_fields", None)
    tmpFields = data.__dict__
    fields = copy(tmpFields)
    if "_state" in fields.keys():
        fields.__delitem__("_state")
    if "id" in fields.keys():
        fields.__delitem__("id")
    if "is_showing" in fields.keys():
        fields.__delitem__("is_showing")
    # 去除字段
    if exclude_fields:
        ex_type = type(exclude_fields)
        if ex_type == list or ex_type == tuple:
            for exclude_field in exclude_fields:
                fields.__delitem__(exclude_field)
        elif ex_type == unicode:
            fields.__delitem__(exclude_fields)

    # 默认转换字段
    for k, v in fields.iteritems():
        if ex_rules and ex_rules.has_key(k):
            fields[k] = ex_rules[k](v)
        if use_choices:
            choices = getattr(data._meta.get_field(k), "choices", None)
            if choices:
                if v is not None:
                    tval = None
                    for choice in choices:
                        if choice[0] == v:
                            tval = choice[1]
                            break
                    if tval is None:
                        tval = "未知"
                else:
                    tval = "暂无"
                fields[k] = tval
        if format_date and type(v) == datetime:
            v += timedelta(hours=8)
            fields[k] = v.strftime('%Y年%m月%d日%H时%M分%S秒')
        if v is None:
            fields[k] = default_str
    # 指定转换字段
    if transform_rules and type(transform_rules) == dict:
        for k, v in transform_rules.iteritems():
            if hasattr(v, '__call__'):
                val = v(fields[k])
                if val is None:
                    fields[k] = "暂无"
                else:
                    fields[k] = val
            elif type(v) == dict:
                fields[k] = v.get(fields[k], "暂无")
            else:
                raise TypeError('invalid transform_rule type:it must be a function or dict')
    return fields.iteritems()
