import logging


def key_gen():
    """
    Generates a random key for bets, placed bets and accounts.
    :return: Random key between 0 and 2147483647 (max size for django's PositiveIntegerField)
    """
    from random import SystemRandom

    randomiser = SystemRandom()
    return randomiser.randint(0, 2147483647)


def get_bet(prim_key):
    """
    Gets the bet corresponding to the primary key. Return None, if no bet with that id exists.
    :param prim_key: Primary key of a bet (ChoiceBet/DateBet)
    :return: The bet (ChoiceBet/DateBet) linked with the primary key or None, if no bet with that primary key exists.
    """
    from bets.models import ChoiceBet, DateBet

    try:
        choice_bet = ChoiceBet.objects.get(prim_key=prim_key)
    except ChoiceBet.DoesNotExist:
        try:
            date_bet = DateBet.objects.get(prim_key=prim_key)
        except DateBet.DoesNotExist:
            return None
        else:
            return date_bet
    else:
        return choice_bet


def get_placed_bet_for_user(bet, user):
    """
    Gets the corresponding placed bet for the user
    :param user: user who might have placed a bet
    :param bet: the bet that it might have been placed on
    :return: the placed bet if one exists, None otherwise
    """
    from django.contrib.auth.models import User
    from bets.models import ChoiceBet, DateBet

    # If we are given a user-object, the we first need to get the corresponding profile
    if isinstance(user, User):
        user = user.profile

    if type(bet) == ChoiceBet:
        bets = bet.placedchoicebet_set.filter(placed_by__exact=user)
    elif type(bet) == DateBet:
        bets = bet.placeddatebet_set.filter(placed_by__exact=user)
    else:
        return None

    if len(bets) == 1:
        return bets[0]
    elif len(bets) > 1:
        logging.error("User had multiple (" + str(len(bets)) + ") placed bets for the same bet. \nUser: " + str(
            user.username) + "\nBet: " + str(bet.prim_key))

        # Still return the first element of the list, so that we have something to work with
        return bets[0]
    else:
        return None


def bet_is_visible_to_user(bet, user):
    """
    Check if a bet is visible to a user.
    :param bet: Bet to check
    :param user: User to check
    :return: True, if the user is not forbidden in the bet and the bet isn't resolved and active
    (already published and still available for bets); False otherwise
    """
    from django.utils import timezone

    if bet.end_bets_date:
        return \
            user not in bet.forbidden.all() and \
            not bet.resolved and \
            bet.pub_date <= timezone.now().date() < bet.end_bets_date
    else:
        return \
            user not in bet.forbidden.all() and \
            not bet.resolved and \
            bet.open_to_bets()


def filter_visible_bets(bets, user):
    """
    Filters a list of bets for user visible bets.
    :param bets: Bets to check
    :param user: User to check
    :return: Filtered list with user visible bets
    """
    filtered_bets = []
    for bet in bets:
        if bet_is_visible_to_user(bet, user):
            filtered_bets.append(bet)
    return filtered_bets


def user_can_place_bet(user, bet):
    """
    Check if a user can bet on a bet.
    :param user: User to check
    :param bet: Bet to check
    :return: True, if the user can see the bet and didn't already bet on it; False otherwiese.
    """
    from profiles.util import user_authenticated
    # Users that are not logged in & verified are not allowed to participate
    if not user_authenticated(user):
        return False

    bet_on = []

    for placed_bet in user.profile.placedchoicebet_set.all():
        bet_on.append(placed_bet.placed_on)

    for placed_bet in user.profile.placeddatebet_set.all():
        bet_on.append(placed_bet.placed_on)

    return bet_is_visible_to_user(bet, user) and (bet not in bet_on)


def filter_index_bets(user, bets):
    """
    Filters a list of bets (available/placed)
    :param user: the user...
    :param bets: list of bets (should all be visible to the user)
    :return: a dictionary of the form:
    {
        'available': [Bet],
        'placed': [PlacedBet]
    }
    """
    filtered_bets = {'available': [], 'placed': []}

    for bet in bets:
        if user_can_place_bet(user, bet):
            filtered_bets['available'].append(bet)
        else:
            filtered_bets['placed'].append(get_placed_bet_for_user(user=user, bet=bet))

    return filtered_bets


def generate_index(user):
    """
    Generates the data for the index for a user
    :param user: the user
    :return: A dictionary of the form:
    {
        'choice_bets': {
            'available': [Bet],
            'placed': [PlacedBet]
        },
        'date_bets': {
            'available': [Bet],
            'placed': [PlacedBet]
        }
    }
    """
    from .models import ChoiceBet, DateBet

    index = {}

    choice_bets = filter_visible_bets(user=user, bets=ChoiceBet.objects.all())
    index['choice_bets'] = filter_index_bets(user=user, bets=choice_bets)

    date_bets = filter_visible_bets(user=user, bets=DateBet.objects.all())
    index['date_bets'] = filter_index_bets(user=user, bets=date_bets)

    return index


def place_bet_transaction(profile, bet, amount):
    """
    Creates and saves a transaction to transfer money when a bet is placed
    :param profile: profile that placed the bet
    :param bet: well... the bet
    :param amount: the amount that was placed
    """
    from bets.models import Bet
    from profiles.models import Profile
    from ledger.util import one_to_one_transaction
    from ledger.exceptions import InsufficientFunds

    if isinstance(profile, Profile):
        username = profile.user.username
        profile = profile.account
    else:
        raise TypeError(
            "place_bet_transaction() needs a Profile object as first argument; got " +
            type(profile).__name__ +
            " instead."
        )

    if isinstance(bet, Bet):
        description = "Placed Bet\nBet: " + str(bet.prim_key) + "\nUser: " + username + "\nAmount: " + str(amount)

        try:
            one_to_one_transaction(
                origin=profile,
                destination=bet.account,
                description=description,
                amount=amount
            )
        except InsufficientFunds:
            logging.info("User has insufficient funds")
    else:
        raise TypeError(
            "place_bet_transaction() needs a Bet object as second argument; got " +
            type(bet).__name__ +
            " instead."
        )


# TODO make generic. What's the type of a date (winning_option)?
def resolve_choice_bet(bet, winning_option):
    """
    Resolves a choice bet and distributes the pot among the user who placed a bet on the winning choice.
    :param bet: Bet to be resolved
    :param winning_option: The winning choice
    """
    # TODO Do we need translations?
    from django.utils.translation import ugettext_lazy as _
    from .models import ChoiceBet, Choice
    from ledger.models import Account
    from ledger.util import one_to_many_transaction
    from ledger.exceptions import InsufficientFunds

    assert isinstance(bet, ChoiceBet)
    assert isinstance(winning_option, Choice)

    placed_bets = bet.placedchoicebet_set.all()
    winning_bets = []

    for placed_bet in placed_bets:
        if placed_bet.chosen == winning_option:
            winning_bets.append(placed_bet)

    # TODO Do we need the int cast? Are bet amounts floats?
    payout = int(bet.account.balance // len(winning_bets))
    server_payout = bet.account.balance % len(winning_bets)
    # TODO let on rain on the server

    winners = []
    for winning_bet in winning_bets:
        winners.append(
            {
                'account': winning_bet.placed_by.account,
                'amount': payout
            }
        )

    winners.append(
        {
            'account': Account.objects.get(name='operator'),
            'amount': payout
        }
    )

    description = "Payout\nBet: " + str(bet.id)
    for winner in winners:
        description += "\nAccount: " + winner['account'].name + ", Amount: " + str(winner['amount'])

    try:
        one_to_many_transaction(origin=bet.account, destinations=winners, description=description)
    except InsufficientFunds:
        raise InsufficientFunds(
            _("The pot division fucked up..."),
            code='i_dun_goofed'
        )
