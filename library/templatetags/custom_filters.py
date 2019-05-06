# coding=utf-8
from django import template
from django.utils.safestring import mark_safe
from django.db import models
from types import FunctionType

register = template.Library()


@register.filter
def append(data, entity):
    return "%s%s" % (data, entity)


@register.filter
def describe(data, choices):
    if data is None:
        return "暂无"
    choices = choices.split(',')
    for choice in choices:
        choice = choice.split(":")
        if len(choice) == 2 and str(data) == choice[0]:
            return choice[1]
    return "未知"


@register.filter
def format_data_str(data, format_str):
    try:
        url = format_str.format(data=data)
    except:
        url = format_str
    return url


@register.filter
def getlist(req, args):
    args = args.split(',')
    result = req.getlist(args[0])
    if len(args) > 1:
        trans_format = args[1]
        if trans_format == "int":
            result = map(lambda i: int(i), result)
    return result


@register.filter
def divide(data, num):
    if isinstance(data, (str, unicode)):
        if data.isdigit():
            data = float(data)
        else:
            data = 0
    return data / num


@register.filter
def getitem(data, key):
    return data.get(key)


@register.filter
def gen_tbody_item(data, entity):
    """
    Returns verbose_name for a field.
    """
    val = data
    handler = None
    if isinstance(entity, tuple):
        key = entity[0]
        handler = entity[-1]
    else:
        key = entity
    for k in key.split('.'):
        if isinstance(val, dict):
            val = val.get(k)
        else:
            choices = []
            if val.__class__.__base__ == models.Model:
                try:
                    choices = getattr(val._meta.get_field(k), "choices", None)
                except:
                    pass
            val = getattr(val, k, None)
            if isinstance(handler, (FunctionType, dict)):
                break
            if choices:
                if val is not None:
                    tval = None
                    for choice in choices:
                        if choice[0] == val:
                            tval = choice[1]
                            break
                    if tval is None:
                        tval = "未知"
                else:
                    tval = "暂无"
                val = tval
        if val is None:
            break
    if isinstance(handler, FunctionType):
        val = handler(val)
    elif isinstance(handler, dict):
        val = handler.get(val, "未知")
    if val is None:
        val = "暂无"
    return val


@register.filter
def gen_operate_item(operate, request):
    if isinstance(operate, tuple):
        a_text = operate[0]
        url = operate[1].format(request=request)
    else:
        if operate in (u"添加", u"新增"):
            url = "../add"
        else:
            url = "#"
        a_text = operate
    return mark_safe("<a href=\"%s\">%s</a>" % (url, a_text))


@register.filter
def gen_row_operate_item(operate, data):
    if isinstance(operate, tuple):
        a_text = operate[0]
        a_url_handle = operate[1]
        if isinstance(a_url_handle, FunctionType):
            url = a_url_handle(data)
        else:
            url = operate[1].format(data=data)
    else:
        if operate == u"详情":
            url = "../%s" % data.id
        elif operate == u"修改":
            url = "../%s/modify" % data.id
        elif operate == u"删除":
            url = "../%s/delete" % data.id
        else:
            url = "#"
        a_text = operate
    if a_text == u'删除':
        return mark_safe(
            "<a href=\"javascript:;\" onclick=$.show_modal_confirm('%s')><span>%s<span></a>" % (url, a_text))
    return mark_safe("<a href=\"%s\"><span>%s<span></a>" % (url, a_text))
