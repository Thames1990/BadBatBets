from django.conf.urls import url
from . import views

urlpatterns = [
    # /bets/
    url(r'^$', views.index, name='index'),
    # /bets/<prim_key>
    url(r'^(?P<prim_key>[0-9]+)/$', views.bets, name='bets'),
]
