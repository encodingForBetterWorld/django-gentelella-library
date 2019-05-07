# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response
from django.views.generic import View
from django import forms
from django.template import RequestContext
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, Page as Dpage
from library.utils.view_utils import general_queryset_order, get_fields
from .forms import ArticleForm, AuthorForm, PublisherForm, ArticlePageForm, ArticleChapterForm, ArticleCatalogueForm, \
    ArticleTagForm, ArticlePageAddForm
from utils.data_utils import get_no_empty_dict
from djangoGentelella import settings
from django.db.models import Q
from .models import Article, Author, Publisher, ArticlePage, ArticleChapter, ArticleCatalogue, ArticleTag
from .serializers import ArticleSerializer, ArticleChapterSerializer, ArticleCatalogueSerializer, ArticlePageSerializer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django.utils.translation import ugettext as _

import json

# Create your views here.
TABLE_BASE_TEMPLATE = "library/base/base_table.html"

STATUS_NO_SUCH_FUNC = "暂无该功能"


def permission_denied(request):
    return render_to_response(
        'library/page_403.html',
        context_instance=RequestContext(request),
        status=403
    )


def page_not_found(request):
    return render_to_response(
        'library/page_404.html',
        context_instance=RequestContext(request),
        status=404
    )


def page_internal_server_error(request):
    return render_to_response(
        'library/page_500.html',
        context_instance=RequestContext(request),
        status=500
    )


def error(request, error_desc, error_msg=None):
    """
    操作失败页面
    :param request:
    :param error_desc:错误信息
    :param error_msg:详细的错误信息（数组）
    :return:
    """
    return render(request, 'library/page_error.html', {"error_msg": error_msg, "error_desc": error_desc})


def success(request, info):
    """
    操作成功页面
    :param request:
    :param info:成功信息
    :return:
    """
    back_step = request.POST.get('back_step')
    return render(request, 'library/page_success.html', {'info': info, 'back_step': back_step})


def paginate(request, data, num=25):
    """
    返回分页数据的响应体
    :param request:
    :param data:
    :param num:
    :param callback:
    :return:
    """
    paginator = Paginator(data, num)
    page = request.GET.get('page')
    try:
        datas = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        datas = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        datas = paginator.page(paginator.num_pages)
    return datas


def render_form(request, title, subtitle, form, operates=None, template='library/base/base_form.html', **kwargs):
    """
    新的通用的表单页面
    :param request:
    :param title:页面标题
    :param subtitle:页面副标题
    :param form:表单
    :return:
    """
    back_step = request.POST.get('back_step', None)
    if back_step is None:
        back_step = -2
    else:
        back_step = int(back_step)
        back_step -= 1
    context = {'title': title, 'subtitle': subtitle, 'form': form, 'operates': operates, 'back_step': back_step}
    if kwargs:
        for k, v in kwargs.iteritems():
            context[k] = v
    return render(request, template, context)


def render_detail(request, prefix, data, fields=None, readonly=True, model_cls=None, template=None):
    """
    通用的详情页面
    :param request:
    :param title:
    :param subtitle:
    :param data:
    :return:
    """
    # 如果传入了数据的ID
    if isinstance(data, int) and model_cls:
        try:
            data = model_cls.objects.get(id=data)
        except ObjectDoesNotExist:
            return error(request, "无法查询到ID为%s的%s" % (data, prefix or "数据"))
        else:
            fields = get_fields(data)
    return render(request, template or "library/base/base_detail_page.html",
                  {'title': prefix, 'subtitle': "在此查看%s的详细信息" % prefix, 'data': data, 'fields': fields,
                   'readonly': readonly})


def index(request):
    """
    首页
    :param request:
    :return:
    """
    return render(request, 'library/index.html')


class Category(object):
    def __init__(self, **kwargs):
        """
        :param name: 业务名称
        :param model: 查询数据时使用的Model
        :param form: 写入数据时使用的Form
        :param add_func: 添加数据的方法，未定义则直接保存数据
        :param modify_form: 修改数据时使用的Form，未指定则使用上一项param
        :param modify_func: 修改数据的方法，未定义则直接修改数据
        :param modify_render_func: 获取修改数据的页面方法，未定义则套用通用模板
        :param detail_render_func: 获取显示详情页方法，未定义则套用通用模板
        :param delete_func：删除数据的方法，未定义则直接删除数据
        :param list_no_search：列表页中不显示搜索框
        :param search_fields: 列表页中搜索框输入后查找的字段
        :param list_no_page：列表页不分页显示
        :param order_field: 列表页中数据的默认排序规则
        :param list_entities：列表页表结构
        :param list_prefix：列表页名称
        :param operates：列表页包含的额外操作列表
        :param row_operates：列表页每行最后一列包含的操作列表
        :param template：列表页模板，默认使用通用模板渲染页面
        :param list_data_handle：列表页中数据如需要特殊处理，指定该项
        :param list_search_const：列表页搜索中如总是需要过滤出特定数据，指定该项
        :param excel_rules：导出excel文件的文件格式
        :param extend_get_funcs：该类URL下除增删改查外的特殊操作类别GET方法
        :param extend_get_sub_funcs：该类URL下除增删改查外的特殊子操作类别GET方法
        :param extend_post_funcs：该类URL下除增删改查外的特殊操作类别POST方法
        :param extend_post_sub_funcs：该类URL下除增删改查外的特殊子操作类别POST方法
        """
        self.name = kwargs.pop('name', None)
        self.model = kwargs.pop('model', None)
        self.form = kwargs.pop('form', None)
        self.add_func = kwargs.pop('add_func', None)
        self.search_fields = kwargs.pop('search_fields', [])
        self.order_field = kwargs.pop('order_field', None)
        self.modify_form = kwargs.pop('modify_form', None)
        self.modify_func = kwargs.pop('modify_func', None)
        self.modify_render_func = kwargs.pop('modify_render_func', None)
        self.detail_render_func = kwargs.pop('detail_render_func', None)
        self.delete_func = kwargs.pop('delete_func', None)
        self.excel_rules = kwargs.pop('excel_rules', None)
        self.extend_get_funcs = kwargs.pop('extend_get_funcs', None)
        self.extend_get_sub_funcs = kwargs.pop('extend_get_sub_funcs', None)
        self.extend_post_funcs = kwargs.pop('extend_post_funcs', None)
        self.extend_post_sub_funcs = kwargs.pop('extend_post_sub_funcs', None)
        self.list_entities = kwargs.pop('list_entities', [])
        self.row_operates = kwargs.pop('row_operates', None)
        self.operates = kwargs.pop('operates', None)
        self.list_prefix = kwargs.pop('list_prefix', None)
        self.list_no_search = kwargs.pop('list_no_search', False)
        self.list_no_page = kwargs.pop('list_no_page', False)
        self.template = kwargs.pop('template', None)
        self.list_data_handle = kwargs.pop('list_data_handle', None)
        self.list_search_const = kwargs.pop('list_search_const', None)
        self.search_template = kwargs.pop('search_template', None)
        if not self.search_fields:
            self.list_no_search = True


class CategoryLibrary(Category):

    def article_detail_render_func(self, request, data, fields):
        prefix = "文章"
        new_fields = {}
        for key, val in fields:
            if key in ('description', 'cover', 'publisher_id'):
                continue
            new_fields[key] = val
        new_fields['tags'] = u"、".join(list(data.tags.all().values_list('name', flat=True)))
        new_fields['authors'] = u"、".join(list(data.authors.all().values_list('name', flat=True)))
        new_fields['publisher'] = data.publisher.name
        return render(request, "library/article_detail_page.html",
                      {'title': prefix,
                       'subtitle': "在此查看%s的详细信息" % prefix,
                       'data': data,
                       'fields': new_fields.iteritems(),
                       'pageForm': ArticlePageAddForm()})

    def __init__(self, model_type):
        super_init = super(CategoryLibrary, self).__init__
        if model_type == 'article':
            super_init(name="文章",
                       model=Article,
                       form=ArticleForm,
                       search_fields=['title'],
                       list_entities=[
                           'title',
                           'subtitle',
                           'publisher',
                           'publish_time'
                       ],
                       operates=[
                           ('新增文章', "../add")
                       ],
                       row_operates=[
                           "详情", "修改", "删除"
                       ],
                       detail_render_func=self.article_detail_render_func,
                       search_template="library/article_table_page.html")
        elif model_type == 'author':
            super_init(name="作者",
                       model=Author,
                       form=AuthorForm,
                       search_fields=['name'],
                       list_entities=[
                           'name',
                           'description'
                       ],
                       operates=[
                           ('新增作者', "../add")
                       ],
                       row_operates=[
                           "详情", "修改", "删除"
                       ])
        elif model_type == 'publisher':
            super_init(name="出版社",
                       model=Publisher,
                       form=PublisherForm,
                       search_fields=['name'],
                       list_entities=[
                           'name',
                           'description'
                       ],
                       operates=[
                           ('新增出版社', "../add")
                       ],
                       row_operates=[
                           "详情", "修改", "删除"
                       ])
        elif model_type == 'article_tag':
            super_init(name="文章分类",
                       model=ArticleTag,
                       form=ArticleTagForm,
                       search_fields=['name'],
                       list_entities=[
                           'name',
                           'description'
                       ],
                       operates=[
                           ('新增分类', "../add")
                       ],
                       row_operates=[
                           "详情", "修改", "删除"
                       ])
        elif model_type == 'article_page':
            super_init(name="书页",
                       model=ArticlePage,
                       form=ArticlePageForm,
                       search_fields=['index'],
                       list_entities=[
                           'index',
                           'article.name'
                       ],
                       operates=[
                           ('新增书页', "../add")
                       ],
                       row_operates=[
                           "详情", "修改"
                       ],
                       list_search_const={
                           "article_id": "{data.article_id}"
                       })
        elif model_type == 'article_chapter':
            super_init(name="章节",
                       model=ArticleChapter,
                       form=ArticleChapterForm,
                       search_fields=['index'],
                       list_entities=[
                           'index',
                           'article.name',
                           'title'
                       ],
                       operates=[
                           ('新增章节', "../add")
                       ],
                       row_operates=[
                           "详情", "修改"
                       ],
                       list_search_const={
                           "article_id": "{data.article_id}"
                       })


class BasePathView(View):
    view_categories = {
        'library': CategoryLibrary
    }

    def handler_path_parameter(self, category, model_type):
        ret = None
        cate_cls = self.view_categories.get(category)
        if cate_cls:
            ret = cate_cls(model_type)
            if not hasattr(ret, "model"):
                ret = None
        return ret

    def handler_id(self, operate_type):
        if operate_type.isdigit():
            operate_type = int(operate_type)
        return operate_type

    def get(self, request, category, model_type, operate_type, sub_operate_type=None):
        model_cate = self.handler_path_parameter(category, model_type)
        if model_cate is None:
            return error(request, STATUS_NO_SUCH_FUNC)
        if operate_type in ("search", "list") and model_cate.model:
            order = request.GET.get('o')
            search = request.GET.get("search")
            kw_str = ""
            for k, v in request.GET.iteritems():
                if k not in ("search", "o", "page"):
                    kw_str += ("%s=%s," % (k, (v.isdigit() or v in ("True", "False")) and v or "\'%s\'" % v))
            ft = model_cate.model.objects
            if kw_str:
                kw_str = kw_str[:-1]
                try:
                    ft = eval("ft.filter(%s)" % kw_str)
                except Exception:
                    pass
            if search:
                search = search.strip()
            if search:
                search_list = search.split("\n")
                search_type = "contains"
                if len(search_list) > 1:
                    search_type = "in"
                    search = search_list
                search_str = ""
                for field in model_cate.search_fields:
                    fis = str(field).split('.')
                    if len(fis) > 1:
                        search_str += "Q("
                        for fi in fis:
                            search_str += (fi + "__")
                        search_str += "%s=search)|" % search_type
                    else:
                        search_str += "Q(%s__%s=search)|" % (field, search_type)
                search_str = search_str[:-1]
                ft = ft.filter(eval(search_str))
            if not order:
                if model_cate.order_field:
                    order = model_cate.order_field
                else:
                    order = None
            datas = general_queryset_order(ft, order).all()
            if not model_cate.list_no_page:
                datas = paginate(request, datas)
            if model_cate.search_template and operate_type == "search":
                return render(request,
                              model_cate.search_template,
                              {"title": model_cate.list_prefix or model_cate.name,
                               "subtitle": "在这里可以查看%s信息，并进行管理" % (model_cate.list_prefix or model_cate.name),
                               "datas": datas,
                               "operates": model_cate.operates,
                               "no_search": model_cate.list_no_search,
                               "no_page": model_cate.list_no_page,
                               "list_search_const": model_cate.list_search_const
                              })
            if model_cate.list_entities:
                if model_cate.list_data_handle:
                    map(model_cate.list_data_handle, datas)
                return render(request,
                              model_cate.template or TABLE_BASE_TEMPLATE,
                              {"title": model_cate.list_prefix or model_cate.name,
                               "subtitle": "在这里可以查看%s信息，并进行管理" % (model_cate.list_prefix or model_cate.name),
                               "datas": datas,
                               "list_entities": model_cate.list_entities,
                               "row_operates": model_cate.row_operates,
                               "operates": model_cate.operates,
                               "no_search": model_cate.list_no_search,
                               "no_page": model_cate.list_no_page,
                               "list_search_const": model_cate.list_search_const
                               })
        elif operate_type == "add":
            if model_cate.form:
                form = model_cate.form()
                return render_form(request, "%s" % model_cate.name, "在此可以添加%s" % model_cate.name, form)
        elif operate_type.isdigit():
            if sub_operate_type and \
                    isinstance(model_cate.extend_get_sub_funcs, dict) and \
                    model_cate.extend_get_sub_funcs.has_key(sub_operate_type):
                extend_get_sub_func = model_cate.extend_get_sub_funcs.get(sub_operate_type)
                return extend_get_sub_func(request, operate_type)
            elif model_cate.model:
                instance_id = self.handler_id(operate_type)
                try:
                    data = model_cate.model.objects.get(id=instance_id)
                except ObjectDoesNotExist:
                    return error(request, "无法在数据库中找到数据")
                except Exception:
                    return error(request, STATUS_NO_SUCH_FUNC)
                if sub_operate_type == "modify":
                    if model_cate.modify_render_func == model_cate.modify_form == model_cate.form == None:
                        return error(request, STATUS_NO_SUCH_FUNC)
                    if model_cate.modify_render_func:
                        return model_cate.modify_render_func(request, data)
                    else:
                        form = None
                        if model_cate.modify_form and model_cate.modify_form.__base__ == forms.ModelForm:
                            form = model_cate.modify_form(instance=data)
                        elif model_cate.form and model_cate.form.__base__ == forms.ModelForm:
                            form = model_cate.form(instance=data)
                        if form:
                            return render_form(request, "%s" % model_cate.name, "在此可以修改%s" % model_cate.name, form)
                elif sub_operate_type == "delete":
                    if model_cate.delete_func:
                        delete_ret = model_cate.delete_func(instance_id, request.session['operator_admin'])
                        if delete_ret:
                            return error(request, delete_ret)
                    else:
                        data.delete()
                    return success(request, "删除%s成功" % model_cate.name)
                elif sub_operate_type is None:
                    if model_cate.detail_render_func:
                        return model_cate.detail_render_func(request, data, get_fields(data))
                    return render_detail(request, model_cate.name, data,
                                         get_fields(data),
                                         readonly=not (model_cate.modify_func or
                                                       model_cate.modify_form or
                                                       (
                                                               model_cate.form and model_cate.form.__base__ == forms.ModelForm)))
        elif isinstance(model_cate.extend_get_funcs, dict):
            extend_get_func = model_cate.extend_get_funcs.get(operate_type)
            if extend_get_func:
                return extend_get_func(request)
        return error(request, STATUS_NO_SUCH_FUNC)

    def post(self, request, category, model_type, operate_type, sub_operate_type=None):
        model_cate = self.handler_path_parameter(category, model_type)
        if model_cate is None:
            return error(request, STATUS_NO_SUCH_FUNC)
        operate_form = model_cate.form
        if operate_type == "add":
            prefix = '添加'
            instance = None
        elif operate_type.isdigit():
            if sub_operate_type and \
                    isinstance(model_cate.extend_post_sub_funcs, dict) \
                    and model_cate.extend_post_sub_funcs.has_key(sub_operate_type):
                extend_post_sub_func = model_cate.extend_post_sub_funcs.get(sub_operate_type)
                return extend_post_sub_func(request, operate_type)
            elif sub_operate_type == "modify" and model_cate.model:
                instance_id = self.handler_id(operate_type)
                if model_cate.modify_form:
                    operate_form = model_cate.modify_form
                prefix = '修改'
                try:
                    instance = model_cate.model.objects.get(id=instance_id)
                except ObjectDoesNotExist:
                    return error(request, "无法在数据库中找到数据")
                if model_cate.modify_func:
                    form = operate_form(request.POST or None, request.FILES)
                    if form.is_valid():
                        modify_fun_result = model_cate.modify_func(request, instance, form)
                        if modify_fun_result:
                            return modify_fun_result
                    else:
                        return render_form(request, "修改%s" % model_cate.name, "在此可以修改%s" % model_cate.name, form)
            else:
                return error(request, STATUS_NO_SUCH_FUNC)
        elif isinstance(model_cate.extend_post_funcs, dict) \
                and model_cate.extend_post_funcs.has_key(operate_type):
            extend_post_func = model_cate.extend_post_funcs.get(operate_type)
            return extend_post_func(request)
        else:
            return error(request, STATUS_NO_SUCH_FUNC)
        if operate_form is None:
            return error(request, STATUS_NO_SUCH_FUNC)
        if operate_form.__base__ == forms.ModelForm:
            form = operate_form(request.POST or None, request.FILES or None, instance=instance)
        else:
            form = operate_form(request.POST or None, request.FILES or None)
        if form.is_valid():
            if isinstance(form, forms.ModelForm):
                data = form.save()
            else:
                data = form
            if operate_type == "add" and model_cate.add_func:
                func_result = model_cate.add_func(request, data)
                if func_result:
                    return func_result
            return success(request, "成功%s%s" % (prefix, model_cate.name))
        else:
            return render_form(request, model_cate.name, "在此可以%s%s" % (prefix, model_cate.name), form)


def common_resp(data, msg, status):
    """
    通用的响应
    :param data:响应内容
    :param msg:响应消息
    :param status:响应状态
    :return:JsonResponse
    """
    return JsonResponse(get_no_empty_dict({'data': data, 'msg': msg, 'status': status}))


def error_resp(msg, data=None):
    """
    通用的错误响应
    :param msg:错误描述
    :param data:错误响应内容
    :return:JsonResponse
    """
    return common_resp(data, msg, settings.STATUS_ERROR)


def success_resp(data, msg, page=None):
    """
    通用的成功响应
    :param data:响应内容
    :param msg:成功描述
    :param integer_status:是否返回整形status，默认为否
    :return:JsonResponse
    """
    ret = {'data': data}
    if isinstance(page, Dpage):
        ret['page'] = {
            "number": page.number,
            "count": page.paginator.count,
            "per_page": page.paginator.per_page,
            "num_pages": page.paginator.num_pages
        }
    return common_resp(ret, msg, settings.STATUS_SUCCESS)


def add_batch_async(request, name, form):
    form_list = request.POST.get('form_list')
    if not form_list:
        return error_resp("无效的参数")
    form_list = json.loads(form_list)
    for idx, dform in enumerate(form_list):
        data = form(dform)
        if data.is_valid():
            data.save()
        else:
            return error_resp(msg='添加第%s条%s失败' % (idx, name))
    return success_resp({}, msg='添加%s成功'% name)


class APICategory(object):
    def list_article_catalogues(self, request, article_id):
        catalogues = ArticleCatalogue.objects.filter(article_id=article_id)
        return success_resp(ArticleCatalogueSerializer(catalogues, many=True).data,
                            _(u"查询文章目录成功"))

    def list_article_chapters(self, request, article_id):
        chapters = ArticleChapter.objects.filter(article_id=article_id)
        return success_resp(ArticleChapterSerializer(chapters, many=True).data,
                            _(u"查询文章章节成功"))

    def list_article_pages(self, request, article_id):
        datas = ArticlePage.objects.filter(article_id=article_id).values_list('id', 'index')
        chapter_id = request.GET.get('chapter_id')
        if chapter_id:
            dpage = paginate(request,
                             ArticlePage.objects.filter(article_id=article_id, chapter_id=chapter_id).values_list('id'),
                             1)
        else:
            dpage = paginate(request, datas, 1)
        data = {}
        if len(dpage.object_list) > 0:
            try:
                data = ArticlePageSerializer(ArticlePage.objects.get(id=dpage.object_list[0][0])).data
            except Exception:
                pass
        return success_resp({
            'data': data,
            'range': list(datas)
        }, _(u"查询文章章节成功"), page=dpage)

    def __init__(self, model_type):
        self.name = ''
        self.model = None
        self.form = None
        self.serializer = None
        self.serializer4list = None
        self.extend_get_funcs = {}
        self.extend_get_sub_funcs = {}
        self.extend_post_funcs = {}
        self.extend_post_sub_funcs = {}
        self.page_size = None
        self.search_fields = []
        self.list_no_search = None
        self.list_no_page = None
        self.list_data_handle = None
        self.modify_form = None
        self.modify_func = None
        self.add_func = None

        if model_type == 'article':
            self.model = Article
            self.serializer = ArticleSerializer
            self.extend_get_sub_funcs = {
                'catalogues': self.list_article_catalogues,
                'chapters': self.list_article_chapters,
                'pages': self.list_article_pages
            }
            self.name = '文章'
        elif model_type == 'catalogue':
            self.model = ArticleCatalogue
            self.form = ArticleCatalogueForm
            self.serializer = ArticleCatalogueSerializer
            self.name = '文章目录'
            self.extend_post_funcs = {
                'add_batch': lambda req: add_batch_async(req, '文章目录', ArticleCatalogueForm)
            }
        elif model_type == 'chapter':
            self.model = ArticleChapter
            self.form = ArticleChapterForm
            self.serializer = ArticleChapterSerializer
            self.name = '文章章节'
            self.extend_post_funcs = {
                'add_batch': lambda req: add_batch_async(req, '文章章节', ArticleChapterForm)
            }
        elif model_type == 'page':
            self.model = ArticlePage
            self.form = ArticlePageForm
            self.serializer = ArticlePageSerializer
            self.name = '书页'

        if not self.search_fields:
            self.list_no_search = True

        self.serializer4list = (isinstance(self.serializer4list,
                                           serializers.ModelSerializer) and self.serializer4list) or (
                                       isinstance(self.serializer,
                                                  serializers.ModelSerializer) and self.serializer)


class BaseAPiView(APIView):
    def handler_id(self, operate_type):
        if operate_type.isdigit():
            operate_type = int(operate_type)
        return operate_type

    def get(self, request, model_type, operate_type, sub_operate_type=None):
        model_cate = APICategory(model_type)
        if model_cate is None:
            return error_resp(STATUS_NO_SUCH_FUNC)
        if operate_type == "list" and model_cate.model:
            order = request.GET.get('o')
            search = request.GET.get("search")
            kw_str = ""
            for k, v in request.GET.iteritems():
                if k not in ("search", "o", "page"):
                    kw_str += ("%s=%s," % (k, (v.isdigit() or v in ("True", "False")) and v or "\'%s\'" % v))
            ft = model_cate.model.objects
            if kw_str:
                kw_str = kw_str[:-1]
                try:
                    ft = eval("ft.filter(%s)" % kw_str)
                except Exception:
                    pass
            if search:
                search = search.strip()
            if search:
                search_list = search.split("\n")
                search_type = "contains"
                if len(search_list) > 1:
                    search_type = "in"
                    search = search_list
                search_str = ""
                for field in model_cate.search_fields:
                    fis = str(field).split('.')
                    if len(fis) > 1:
                        search_str += "Q("
                        for fi in fis:
                            search_str += (fi + "__")
                        search_str += "%s=search)|" % search_type
                    else:
                        search_str += "Q(%s__%s=search)|" % (field, search_type)
                search_str = search_str[:-1]
                ft = ft.filter(eval(search_str))
            if not order:
                if model_cate.order_field:
                    order = model_cate.order_field
                else:
                    order = None
            datas = general_queryset_order(ft, order).all()
            dpage = None
            if isinstance(model_cate.serializer4list, serializers.ModelSerializer):
                if model_cate.list_data_handle:
                    map(model_cate.list_data_handle, datas)
                if not model_cate.list_no_page:
                    dpage = paginate(request, datas)
                    datas = model_cate.serializer4list(dpage, many=True).data
                else:
                    datas = model_cate.serializer4list(datas, many=True).data
                return success_resp(datas, _(u"查询%s列表成功" % model_cate.name), page=dpage)

        elif operate_type.isdigit():
            if sub_operate_type and \
                    model_cate.extend_get_sub_funcs.has_key(sub_operate_type):
                extend_get_sub_func = model_cate.extend_get_sub_funcs.get(sub_operate_type)
                return extend_get_sub_func(request, operate_type)
            if model_cate.model:
                instance_id = self.handler_id(operate_type)
                try:
                    data = model_cate.model.objects.get(id=instance_id)
                except ObjectDoesNotExist:
                    return error_resp(_(u"无法在数据库中找到数据"))
                except Exception:
                    return error_resp(STATUS_NO_SUCH_FUNC)
                if sub_operate_type is None and isinstance(model_cate.serializer, serializers.ModelSerializer):
                    return success_resp(model_cate.serializer(data).data, _(u"查询%s成功" % model_cate.name))
        elif model_cate.extend_get_funcs.has_key(operate_type):
            extend_get_func = model_cate.extend_get_funcs.get(operate_type)
            if extend_get_func:
                return extend_get_func(request)
        return error_resp(STATUS_NO_SUCH_FUNC)

    def post(self, request, model_type, operate_type, sub_operate_type=None):
        model_cate = APICategory(model_type)
        if model_cate is None:
            return error_resp(STATUS_NO_SUCH_FUNC)
        operate_form = model_cate.form
        if operate_type == "add":
            prefix = '添加'
            instance = None
        elif operate_type.isdigit():
            if sub_operate_type and \
                    model_cate.extend_post_sub_funcs.has_key(sub_operate_type):
                extend_post_sub_func = model_cate.extend_post_sub_funcs.get(sub_operate_type)
                return extend_post_sub_func(request, operate_type)
            elif sub_operate_type in ("delete", "modify") and model_cate.model:
                instance_id = self.handler_id(operate_type)
                try:
                    instance = model_cate.model.objects.get(id=instance_id)
                except ObjectDoesNotExist:
                    return error_resp(_(u"无法在数据库中找到数据"))
                if sub_operate_type == "modify":
                    prefix = '修改'
                    if model_cate.modify_form:
                        operate_form = model_cate.modify_form
                    if model_cate.modify_func:
                        form = operate_form(request.POST or None, request.FILES)
                        if form.is_valid():
                            modify_fun_result = model_cate.modify_func(request, instance, form)
                            if modify_fun_result:
                                return modify_fun_result
                        else:
                            return error_resp(_(u"修改%s失败" % model_cate.name))
                else:
                    try:
                        instance.delete()
                    except Exception:
                        return error_resp(_(u"删除%s失败" % model_cate.name))
                    else:
                        return success_resp({}, _(u"删除%s成功" % model_cate.name))
            else:
                return error_resp(STATUS_NO_SUCH_FUNC)
        elif model_cate.extend_post_funcs.has_key(operate_type):
            extend_post_func = model_cate.extend_post_funcs.get(operate_type)
            return extend_post_func(request)
        else:
            return error_resp(STATUS_NO_SUCH_FUNC)
        if operate_form is None:
            return error_resp(STATUS_NO_SUCH_FUNC)
        if operate_form.__base__ == forms.ModelForm:
            form = operate_form(request.POST or None, request.FILES or None, instance=instance)
        else:
            form = operate_form(request.POST or None, request.FILES or None)
        if form.is_valid():
            if isinstance(form, forms.ModelForm):
                data = form.save()
            else:
                data = form
            if operate_type == "add" and model_cate.add_func:
                func_result = model_cate.add_func(request, data)
                if func_result:
                    return func_result
            return success_resp({}, _(u"成功%s%s" % (prefix, model_cate.name)))
        else:
            return error_resp(_(u"修改%s失败" % model_cate.name))