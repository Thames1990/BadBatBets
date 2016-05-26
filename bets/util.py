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


def get_bet_for_user(bet, user):
    """
    Finds a placed bet made by that user on that bet.
    :param bet: Bet the user has bet on or not
    :param user: User
    :return: The placed bet the user has bet on for bet.
    """
    from bets.models import ChoiceBet, DateBet

    if type(bet) == ChoiceBet:
        bets = bet.placedchoicebet_set.filter(placed_by__exact=user.profile)
    elif type(bet) == DateBet:
        bets = bet.placeddatebet_set.filter(placed_by__exact=user.profile)
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

    if bet.pub_date and bet.end_bets_date:
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
    filtered_bets = {'available': [], 'placed': []}

    for bet in bets:
        if user_can_place_bet(user, bet):
            filtered_bets['available'].append(bet)
        else:
            filtered_bets['placed'].append(bet)

    return filtered_bets


def generate_index(user):
    from .models import ChoiceBet, DateBet

    index = {}

    choice_bets = filter_visible_bets(user=user, bets=ChoiceBet.objects.all())
    index['choice_bets'] = filter_index_bets(user=user, bets=choice_bets)

    date_bets = filter_visible_bets(user=user, bets=DateBet.objects.all())
    index['date_bets'] = filter_index_bets(user=user, bets=date_bets)

    return index
