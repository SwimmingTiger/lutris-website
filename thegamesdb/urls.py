# pylint: disable=E1120, C0103
from django.conf.urls import url
from thegamesdb import views


urlpatterns = [
    url(r'^$', views.search, name='tgb.search'),
    url(r'^(\d+)$', views.detail, name='tgb.detail'),
]