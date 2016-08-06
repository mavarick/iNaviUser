"""TagSys URL Configuration

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

from views_api import api_add_tag, api_add_target, api_search_target, api_search_target_by_tag, \
    api_update_target, api_delete_target, api_delete_target_tag


urlpatterns = [
    # views

    # url(r'^admin/', admin.site.urls),
    url(r'api/add_tag', api_add_tag, name="api_add_tag"),
    url(r'api/add_target', api_add_target, name="api_add_target"),
    url(r'api/search_target', api_search_target, name="api_search_target"),
    url(r'api/search_tag', api_search_target_by_tag, name="api_search_target_by_tag"),
    url(r'api/delete_target', api_delete_target, name="delete_target"),
    url(r'api/delete_target_tag', api_delete_target_tag, name="api_delete_target_tag"),
    url(r'api/update_target', api_update_target, name="api_update_target"),

    #
]
