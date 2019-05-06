from django.conf.urls import url, include
from .views import BasePathView, BaseAPiView, index

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^api/(?P<model_type>\w+)/(?P<operate_type>\w+)/(?:(?P<sub_operate_type>\w+))?$', BaseAPiView.as_view(),
        name='api'),
    url(r'^(?P<category>\w+)/(?P<model_type>\w+)/(?P<operate_type>\w+)/(?:(?P<sub_operate_type>\w+))?$',
        BasePathView.as_view(), name='base_path')
]
