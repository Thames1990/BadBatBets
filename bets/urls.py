from django.conf.urls import url

from . import views

app_name = 'bets'

urlpatterns = [
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
        views.resolve_bet_view,
        name='resolve_bet'
    ),

    # Create ChoiceBet
    url(
        r'create/choice/$',
        views.create_choice_bet,
        name='create_choice_bet'
    ),

    # Edit ChoiceBet
    url(
        r'^(?P<pk>[0-9]+)/edit/$',
        views.ChoiceBetUpdate.as_view(),
        name="edit_choice_bet"
    ),

    # Delete ChoiceBet
    url(
        r'^(?P<pk>[0-9]+)/delete/$',
        views.ChoiceBetDelete.as_view(),
        name="delete_choice_bet"
    ),

    # Create DateBet
    url(
        r'^create/date/$',
        views.create_date_bet,
        name="create_date_bet"
    ),

    # Edit DateBet
    url(
        r'^(?P<pk>[0-9]+)/edit/$',
        views.DateBetUpdate.as_view(),
        name="edit_date_bet"
    ),

    # Delete DateBet
    url(
        r'^(?P<pk>[0-9]+)/delete/$',
        views.DateBetDelete.as_view(),
        name="delete_date_bet"
    ),
]
