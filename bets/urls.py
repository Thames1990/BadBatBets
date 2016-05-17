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

    # /bets/<prim_key>/voted
    url(
        r'^(?P<prim_key>[0-9]+)/voted$',
        views.choice_bet_view,
        name='choice_bet'
    ),

    url(
        r'^create/choice/$',
        views.create_choice_bet,
        name="create_choice"
    ),
]
