from django.conf.urls import url

from . import views

app_name = 'bets'

urlpatterns = [
    # /bets/
    url(
        r'^$',
        views.index_view,
        name='index'
    ),

    # /bets/<prim_key>
    url(
        r'^(?P<prim_key>[0-9]+)/$',
        views.bet_view,
        name='bet'
    ),

    # /bets/<prim_key>/bet
    url(
        r'^(?P<prim_key>[0-9]+)/bet$',
        views.place_bet,
        name='place_bet'
    ),

    url(
        r'^create/date/$',
        views.create_date_bet,
        name="create_date_bet"
    ),
]
