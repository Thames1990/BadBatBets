from django.conf.urls import url

from . import views

app_name = 'bets'

urlpatterns = [
    # Index page
    url(
        r'^$',
        views.index_view,
        name='index'
    ),

    # Bet page
    url(
        r'^(?P<prim_key>[0-9]+)/$',
        views.bet_view,
        name='bet'
    ),

    # Place a bet
    url(
        r'^(?P<prim_key>[0-9]+)/bet$',
        views.place_bet,
        name='place_bet'
    ),

    # Resolve a bet
    url(
        r'^(?P<prim_key>[0-9]+)/resolve$',
        views.resolve_bet,
        name='resolve_bet'
    ),

    # Create ChoiceBet
    url(
        r'create/choice/$',
        views.create_choice_bet,
        name='create_choice_bet'
    ),

    # Create DateBet
    url(
        r'^create/date/$',
        views.create_date_bet,
        name="create_date_bet"
    ),
]
