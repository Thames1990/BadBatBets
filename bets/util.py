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
    from profiles.models import Profile
    from journal.models import Entry

    profile = Profile.objects.get(pk=user)

    if type(bet) == ChoiceBet:
        bets = bet.placedchoicebet_set.filter(placed_by__exact=profile)
    elif type(bet) == DateBet:
        bets = bet.placeddatebet_set.filter(placed_by__exact=profile)
    else:
        return None

    if len(bets) == 1:
        return bets[0]
    elif len(bets) > 1:
        # Put an entry into the journal so that we know, that there's a problem
        name = "Multiple PlacedBets for User"
        content = "User had multiple (" + str(len(bets)) + ") placed bets for the same bet. \nUser: " + str(user.username) + "\nBet: " + str(bet.prim_key)
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
