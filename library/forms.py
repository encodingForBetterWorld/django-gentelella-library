# coding=utf-8
from .models import *
from django import forms
from library.utils.widgets import LabelautySelect, LabelautyMultipleSelect, GentelellaDatePicker


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'
        exclude = ["create_time"]


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = '__all__'
        exclude = ["create_time"]


class ArticleTagForm(forms.ModelForm):
    class Meta:
        model = ArticleTag
        fields = '__all__'
        exclude = ["create_time"]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        exclude = ["create_time"]

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['publish_time'] = forms.DateTimeField(label="出版时间", widget=GentelellaDatePicker())
        self.fields['authors'] = forms.ModelMultipleChoiceField(label="作者", queryset=Author.objects.all(),
                                                                required=False, widget=LabelautyMultipleSelect())
        self.fields['publisher'] = forms.ModelChoiceField(label="出版社", queryset=Publisher.objects.all(),
                                                          required=False, widget=LabelautySelect())
        self.fields['tags'] = forms.ModelMultipleChoiceField(label="分类", queryset=ArticleTag.objects.all(),
                                                             required=False, widget=LabelautyMultipleSelect())


class ArticleContentForm(forms.ModelForm):

    def is_valid(self):
        instance = self.instance
        if isinstance(instance.index, int) and instance.article and (instance.id is None):
            query_set = getattr(instance.article, instance.__class__.__name__.lower() + '_set', None)
            if query_set is None:
                return
            if query_set.filter(index=instance.index).count() > 0:
                query_set.filter(index__gte=instance.index).update(index=models.F('index')+1)
        return super(ArticleContentForm, self).is_valid()


class ArticleChapterForm(ArticleContentForm):
    class Meta:
        model = ArticleChapter
        fields = '__all__'
        exclude = ["article_id"]


class ArticlePageForm(ArticleContentForm):
    class Meta:
        model = ArticlePage
        fields = '__all__'
        exclude = ["article_id", "chapter_id"]


class ArticlePageAddForm(forms.ModelForm):
    class Meta:
        model = ArticlePage
        fields = ['content']


class ArticleCatalogueForm(ArticleContentForm):
    class Meta:
        model = ArticleCatalogue
        fields = '__all__'

