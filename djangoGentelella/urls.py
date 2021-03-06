"""djangoGentelella URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
import settings
from library.views import page_not_found, permission_denied, page_internal_server_error

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'', include('library.urls')),
    # url(r'^media/(?P<path>.*)$', serve,
    #     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    # url(r'^static/(?P<path>.*)$', serve,
    #     {'document_root': settings.STATIC_ROOT})
]
handler403 = permission_denied
handler404 = page_not_found
handler500 = page_internal_server_error
