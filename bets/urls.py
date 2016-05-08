from django.conf.urls import url
from . import views

app_name = 'bets'

urlpatterns = [
    # /bets/
    url(
        r'^$',
        views.IndexView.as_view(),
        name='index'
    ),

    # /bets/<prim_key>
    url(
        r'^(?P<pk>[0-9]+)/$',
        views.BetView.as_view(),
        name='bet'
    ),

    # /bets/<prim_key>/voted
    url(
        r'^(?P<prim_key>[0-9]+)/voted$',
        views.choice_bet_view,
        name='choice_bet'
    ),

    # /bets/create/
    url(
        r'^create/$',
        views.BetCreate.as_view(),
        name='create_bet'
    ),

    url(
        r'(?P<pk>[0-9]+)/update$',
        views.BetUpdate.as_view(),
        name='update_bet'
    ),

    url(
        r'(?P<pk>[0-9]+)/delete$',
        views.BetDelete.as_view(),
        name='delete_bet'
    ),
]
