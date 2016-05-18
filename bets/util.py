import logging


def pkgen():
    from random import SystemRandom

    randomiser = SystemRandom()
    # 2147483647 is the largest values supported by django's PositiveIntegerField
    return randomiser.randint(0, 2147483647)


def get_bet(id):
    """Gets the bet corresponding to the id. Return None, if not bet with that id exists"""
    from bets.models import ChoiceBet, DateBet

    bet = ChoiceBet.objects.filter(prim_key=id)
    if len(bet) > 0:
        return bet[0]

    bet = DateBet.objects.filter(prim_key=id)
    if len(bet) > 0:
        return bet[0]

    return None


def get_bet_for_user(bet, user):
    """Finds a placed bet made by that user on that bet"""
    from bets.models import ChoiceBet, DateBet
    from journal.models import Entry

    if type(bet) == ChoiceBet:
        bets = bet.placedchoicebet_set.filter(placed_by__exact=user.profile)
    elif type(bet) == DateBet:
        bets = bet.placeddatebet_set.filter(placed_by__exact=user.profile)
    else:
        return None

    if len(bets) == 1:
        return bets[0]
    elif len(bets) > 1:
        # Put an entry into the journal so that we know, that there's a problem
        name = "Multiple PlacedBets for User"
        content = "User had multiple (" + str(len(bets)) + ") placed bets for the same bet. \nUser: " + str(
            user.username) + "\nBet: " + str(bet.prim_key)
        raised_by = "get_bet_for_users"

        journal_entry = Entry(name=name, content=content, raised_by=raised_by)
        journal_entry.save()

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
        return user not in bet.forbidden.all() and not bet.resolved and bet.pub_date <= timezone.now().date() < bet.end_bets_date
    else:
        return user not in bet.forbidden.all() and not bet.resolved and bet.pub_date <= timezone.now().date()


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


def user_can_bet_on_bet(user, bet):
    """
    Check if a user can bet on a bet.
    :param user: User to check
    :param bet: Bet to check
    :return: True, if the user can see the bet and didn't already bet on it; False otherwiese.
    """
    logger = logging.getLogger(__name__)

    logger.debug("Bet name: " + bet.name)
    logger.debug("Is visible: " + str(bet_is_visible_to_user(bet, user)))
    logger.debug("Already bet on bet: " + str(bet in user.profile.placedchoicebet_set.all()))

    # TODO fix didn't bet on this yet
    return bet_is_visible_to_user(bet, user) and \
           bet not in user.profile.placedchoicebet_set.all() and \
           bet not in user.profile.placeddatebet_set.all()
