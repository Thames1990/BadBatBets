from django.conf.urls import url
from . import views

urlpatterns = [
    # Index
    url(r'^$', views.index, name='index'),
    # Open specific bet by id
    url(r'^(?P<prim_key>[0-9]+)/$', views.bets, name='bets'),
]
