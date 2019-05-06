import models
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Article
        fields = "__all__"


class ArticleChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArticleChapter
        fields = "__all__"


class ArticlePageSerializer(serializers.ModelSerializer):
    chapter = ArticleChapterSerializer(read_only=True)

    class Meta:
        model = models.ArticlePage
        fields = "__all__"


class ArticleCatalogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArticleCatalogue
        fields = "__all__"
