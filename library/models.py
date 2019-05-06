# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField


# Create your models here.

class FakeDeleteModalManager(models.Manager):
    def all(self):
        return super(FakeDeleteModalManager, self).filter(is_showing=True).all()


class FakeDeleteModal(models.Model):
    is_showing = models.BooleanField(editable=False, default=True, blank=True)
    objects = FakeDeleteModalManager()

    def delete(self, **kwargs):
        self.is_showing = False
        return super(FakeDeleteModal, self).save()

    class Meta:
        abstract = True


class Author(FakeDeleteModal):
    name = models.CharField(max_length=100, verbose_name="姓名", null=True)
    description = models.CharField(max_length=1000, verbose_name="描述信息", null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=True)

    class Meta:
        verbose_name = "作者"
        verbose_name_plural = "作者"

    def __unicode__(self):
        return self.name


class Publisher(FakeDeleteModal):
    name = models.CharField(max_length=100, verbose_name="名称", null=True)
    description = models.CharField(max_length=1000, verbose_name="描述信息", null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=True)

    class Meta:
        verbose_name = "出版社"
        verbose_name_plural = "出版社"

    def __unicode__(self):
        return self.name


class ArticleTag(FakeDeleteModal):
    name = models.CharField(max_length=100, verbose_name="名称", null=True)
    description = models.CharField(max_length=1000, verbose_name="描述信息", null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=True)

    class Meta:
        verbose_name = "书籍分类"
        verbose_name_plural = "书籍分类"

    def __unicode__(self):
        return self.name


class Article(FakeDeleteModal):
    title = models.CharField(max_length=100, verbose_name="书名", null=True)
    subtitle = models.CharField(max_length=100, verbose_name="副标题", null=True)
    description = RichTextField(verbose_name="简介", null=True)
    cover = models.FileField(upload_to="covers", verbose_name="封面图片", blank=True)
    authors = models.ManyToManyField(Author, verbose_name="作者", null=True)
    tags = models.ManyToManyField(ArticleTag, verbose_name="分类", null=True)
    publish_code = models.CharField(max_length=100, verbose_name="出版编号", null=True)
    publish_time = models.DateTimeField(verbose_name="出版时间", null=True)
    publisher = models.ForeignKey(Publisher, verbose_name="出版社", on_delete=models.SET_NULL, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=True)

    class Meta:
        verbose_name = "书籍"
        verbose_name_plural = "书籍"

    def __unicode__(self):
        return self.title


class ArticleChapter(models.Model):
    class Meta:
        ordering = ['index']
        verbose_name = "章节"
        verbose_name_plural = "章节"

    index = models.IntegerField(verbose_name="章节编号", null=True)
    title = models.CharField(max_length=100, verbose_name="标题", null=True)
    description = models.CharField(max_length=2000, verbose_name="简介", null=True, blank=True)
    article = models.ForeignKey(Article, verbose_name="书籍", on_delete=models.SET_NULL, null=True)

    def __unicode__(self):
        return '{0}:{1}'.format(self.index, self.title)


class ArticlePage(models.Model):
    class Meta:
        ordering = ['index']
        verbose_name = "书页"
        verbose_name_plural = "书页"
    index = models.IntegerField(verbose_name="页码", null=True)
    content = RichTextField(verbose_name="内容", null=True)
    article = models.ForeignKey(Article, verbose_name="书籍", on_delete=models.SET_NULL, null=True)
    chapter = models.ForeignKey(ArticleChapter, verbose_name="所属章节", on_delete=models.SET_NULL, null=True, blank=True)

    def __unicode__(self):
        return self.index


class ArticleCatalogue(models.Model):
    class Meta:
        ordering = ['index']
        verbose_name = "书籍目录"
        verbose_name_plural = "书籍目录"

    index = models.IntegerField(verbose_name="页码", null=True)
    index_description = models.CharField(max_length=100, verbose_name="页码描述", null=True, blank=True)
    title = models.CharField(max_length=100, verbose_name="标题", null=True)
    description = models.CharField(max_length=2000, verbose_name="简介", null=True, blank=True)
    page = models.ForeignKey(ArticlePage, verbose_name="书页", on_delete=models.SET_NULL, null=True, blank=True)
    article = models.ForeignKey(Article, verbose_name="书籍", on_delete=models.SET_NULL, null=True)

    def __unicode__(self):
        return self.name
