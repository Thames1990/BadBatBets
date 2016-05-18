def pkgen():
    from random import SystemRandom

    randomiser = SystemRandom()
    # 2147483647 is the largest values supported by django's PositiveIntegerField
    return randomiser.randint(0, 2147483647)


def get_bet(id):
    """Gets the bet corresponding to the id. Returns None, if no bet with that id exists"""
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
        # TODO: log shit

        # Still return the first element of the list, so that we have something to work with
        return bets[0]
    else:
        return None
