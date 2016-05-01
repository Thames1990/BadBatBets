from django.conf.urls import url
from . import views

app_name = 'bets'

urlpatterns = [
    # /bets/
    url(r'^$', views.index, name='index'),
    # /bets/<prim_key>
    url(r'^(?P<prim_key>[0-9]+)/$', views.binary_bet, name='binary_bet'),
    # /bets/<prim_key>/placed/
    url(r'^(?P<prim_key>[0-9]+)/placed/$', views.placed_binary_bet, name='placed_binary_bet'),
]
