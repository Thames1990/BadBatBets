def pkgen():
    from random import SystemRandom

    randomiser = SystemRandom()
    # 2147483647 is the largest values supported by django's PositiveIntegerField
    return randomiser.randint(0, 2147483647)


def get_bet(prim_key):
    """Gets the bet corresponding to the primary key. Return None, if no bet with that primary key exists"""
    from bets.models import ChoiceBet, DateBet

    bet = ChoiceBet.objects.filter(prim_key=prim_key)
    if len(bet) > 0:
        return bet[0]

    bet = DateBet.objects.filter(prim_key=prim_key)
    if len(bet) > 0:
        return bet[0]

    return None


def get_bet_for_user(bet, user):
    """Finds a placed bet made by that user on that bet"""
    from bets.models import ChoiceBet, DateBet
    from profiles.models import Profile

    profile = Profile.objects.get(pk=user)

    if type(bet) == ChoiceBet:
        bets = bet.placedchoicebet_set.filter(placed_by__exact=profile)
    elif type(bet) == DateBet:
        bets = bet.placeddatebet_set.filter(placed_by__exact=profile)
    else:
        return None

    if len(bets) == 0:
        return None
    elif len(bets) > 1:
        # TODO: Notify admins that something is wrong.
        return bets[0]
    else:
        return bets[0]


def bet_is_visible_to_user(bet, user):
    """
    Check if a bet is visible to a user.
    :param bet: Bet to check
    :param user: User to check
    :return: True, if the user is not forbidden in the bet and the bet isn't resolved and active
    (already published and still available for bets); False otherwise
    """
    from profiles.models import Profile
    from django.utils import timezone

    profile = Profile.objects.get(pk=user)

    return profile.user not in bet.forbidden and \
           bet.resolved is not False and \
           bet.pub_date <= timezone.now() < bet.end_bets_date


def user_can_bet_on_bet(user, bet):
    """
    Check if a user can bet on a bet.
    :param user: User to check
    :param bet: Bet to check
    :return: True, if the user can see the bet and didn't already bet on it; False otherwiese.
    """
    from profiles.models import Profile

    profile = Profile.objects.get(pk=user)

    return bet_is_visible_to_user(bet, user) and \
           bet not in profile.placedchoicebet_set and \
           bet not in profile.placeddatebet_set
