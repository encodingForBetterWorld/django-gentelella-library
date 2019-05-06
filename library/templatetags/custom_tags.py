# coding=utf-8
from django import template
from django.db import models
from django.core.paginator import Page
import re
MAX_PAGE_RANGE = 6
register = template.Library()


@register.inclusion_tag("tags/sortable_table_head.html")
def sortable_table_head(query_str, field_name, head_name):
    sortable = True
    order_head = {}
    reg = "((?<=o\=).*(?=&))|((?<=o\=).*&?)"
    o = re.search(re.compile(reg, re.S), query_str)
    if o:
        o = o.group()
    reg = "&?o=.*&?"
    query_str = re.subn(re.compile(reg, re.S), '', query_str)[0]
    if sortable:
        show_mode = 2
        if o:
            if o == field_name:
                show_mode = 1
                if query_str != '':
                    href_url = '?%s&o=-%s' % (query_str, field_name)
                else:
                    href_url = '?o=-%s' % field_name
            elif o == '-' + field_name:
                show_mode = 0
                href_url = '?%s' % query_str
        if show_mode == 2:
            if query_str != '':
                href_url = '?%s&o=%s' % (query_str, field_name)
            else:
                href_url = '?o=%s' % field_name
        order_head['show_mode'] = show_mode
        order_head['href_url'] = href_url
    order_head['head_name'] = head_name
    order_head['sortable'] = sortable
    return order_head


@register.inclusion_tag("tags/sortable_table_heads.html")
def sortable_table_heads(query_str, page, list_entities, has_row_operate, no_sortable):
    reg = "((?<=o\=).*(?=&))|((?<=o\=).*&?)"
    o = re.search(re.compile(reg, re.S), query_str)
    if o:
        o = o.group()
    reg = "&?o=.*&?"
    query_str = re.subn(re.compile(reg, re.S), '', query_str)[0]
    order_heads = []
    with_param = False
    if isinstance(list_entities, (str, unicode)):
        model_cls = None
        tmp = []
        for item in list_entities.split(","):
            tmp.append(item.split(":"))
        list_entities = tmp
        with_param = True
    else:
        if isinstance(page, Page):
            object_list = page.object_list
        else:
            object_list = page
        if isinstance(object_list, list):
            model_cls = None
            if len(object_list) > 0 and isinstance(object_list[0], models.Model):
                model_cls = object_list[0]._meta
        else:
            model_cls = object_list.model._meta
    for list_entity in list_entities:
        sortable = not no_sortable
        head_name = None
        if isinstance(list_entity, (tuple,list)):
            field_name = list_entity[0]
            if isinstance(list_entity[1], (str,unicode)):
                head_name = list_entity[1]
        else:
            field_name = list_entity
        if "." in field_name:
            sortable = with_param
        elif head_name is None and model_cls:
            try:
                head_name = model_cls.get_field(field_name).verbose_name.title()
            except:
                sortable = False
        order_head = {}
        if sortable:
            show_mode = 2
            if o:
                if o == field_name:
                    show_mode = 1
                    if query_str != '':
                        href_url = '?%s&o=-%s' % (query_str, field_name)
                    else:
                        href_url = '?o=-%s' % field_name
                elif o == '-'+field_name:
                    show_mode = 0
                    href_url = '?%s' % query_str
            if show_mode == 2:
                if query_str != '':
                    href_url = '?%s&o=%s' % (query_str, field_name)
                else:
                    href_url = '?o=%s' % field_name
            order_head['show_mode'] = show_mode
            order_head['href_url'] = href_url
        order_head['head_name'] = head_name
        order_head['sortable'] = sortable
        order_heads.append(order_head)
    if has_row_operate:
        order_heads.append({"head_name":"相关操作",
                            "sortable":False})
    return {"order_heads": order_heads}


@register.inclusion_tag("tags/pagination.html")
def pagination(query_str, page):
    curr_idx = page.number
    last_idx = page.paginator.num_pages
    if last_idx <= MAX_PAGE_RANGE:
        page_indexes = range(1, last_idx + 1)
    else:
        mid_idx = MAX_PAGE_RANGE/2 + 1
        last_mid_idx = last_idx - (MAX_PAGE_RANGE - mid_idx)
        if curr_idx <= mid_idx:
            page_indexes = range(1, MAX_PAGE_RANGE + 1)
        elif curr_idx > last_mid_idx:
            page_indexes = range(last_idx+1-MAX_PAGE_RANGE,last_idx + 1)
        else:
            page_indexes = range(curr_idx-mid_idx+1, curr_idx+MAX_PAGE_RANGE-mid_idx+1)
    return {"sum": page.paginator.count,
            "current_index": page.number,
            "page_indexes": page_indexes,
            "num_pages": page.paginator.num_pages,
            "start_index": page.start_index(),
            "end_index": page.end_index(),
            "has_previous":page.has_previous(),
            "has_next":page.has_next(),
            "query_string":re.compile(r"&?page\=\d+").sub("", query_str)}


@register.inclusion_tag("tags/pagination_select.html")
def pagination_select(query_str, page):
    return {"sum": page.paginator.count,
            "current_index": page.number,
            "page_indexes": list(range(1, page.paginator.num_pages+1)),
            "num_pages": page.paginator.num_pages,
            "start_index": page.start_index(),
            "end_index": page.end_index(),
            "has_previous":page.has_previous(),
            "has_next":page.has_next(),
            "query_string":re.compile(r"&?page\=\d+").sub("", query_str)}


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name.title()