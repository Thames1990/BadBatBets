import logging

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


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


def get_placed_bet_for_profile(bet, profile):
    """
    Gets the corresponding placed bet for the profile.
    :param profile: Profile who might have placed a bet
    :param bet: The bet that it might have been placed on
    :return: The placed bet if one exists, None otherwise
    """
    from profiles.models import Profile
    from bets.models import Bet, ChoiceBet, DateBet

    assert isinstance(bet, Bet)
    assert isinstance(profile, Profile)

    if isinstance(bet, ChoiceBet):
        bets = bet.placedchoicebet_set.filter(placed_by__exact=profile)
    elif isinstance(bet, DateBet):
        bets = bet.placeddatebet_set.filter(placed_by__exact=profile)
    else:
        logger.warning("Tried to get placed bets for unknown bet type with bet (" + bet + ").")
        return None

    if len(bets) == 1:
        return bets[0]
    elif len(bets) > 1:
        logger.error("User had multiple (" + str(len(bets)) + ") placed bets for the same bet. \nUser: " + str(
            profile.username) + "\nBet: " + str(bet.prim_key))

        # Still return the first element of the list, so that we have something to work with
        return bets[0]
    else:
        return None


def get_choice(description):
    """
    Gets a choice by description.
    :param description: Description of the searched choice
    :return: The choice, if a fitting choice exists for the given description; None otherwise.
    """
    from bets.models import Choice

    try:
        choice = Choice.objects.get(description=description)
    except Choice.DoesNotExist:
        return None
    else:
        return choice


def bet_is_visible_to_user(bet, user):
    """
    Check if a bet is visible to a user.
    :param bet: Bet to check
    :param user: User to check
    :return: True, if the user is not forbidden in the bet and the bet isn't resolved and active
    (already published and still available for bets); False otherwise
    """
    from django.contrib.auth.models import User
    from django.utils import timezone
    from .models import Bet

    assert isinstance(bet, Bet)
    assert isinstance(user, User)

    forbidden_accounts = []

    for forbidden_user in bet.forbidden.all():
        if forbidden_user.has_account:
            forbidden_accounts.append(forbidden_user.account.user)

    if bet.end_bets_date:
        return \
            user not in forbidden_accounts and \
            not bet.resolved and \
            bet.pub_date <= timezone.now().date() < bet.end_bets_date
    else:
        return \
            user not in forbidden_accounts and \
            not bet.resolved and \
            bet.open_to_bets()


def filter_visible_bets(bets, user):
    """
    Filters a list of bets for user visible bets.
    :param bets: Bets to check
    :param user: User to check
    :return: Filtered list with user visible bets
    """
    from django.contrib.auth.models import User

    assert isinstance(user, User)

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
    from django.contrib.auth.models import User
    from .models import Bet
    from profiles.util import user_authenticated

    assert isinstance(user, User)
    assert isinstance(bet, Bet)

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
    from django.contrib.auth.models import User

    assert isinstance(user, User)

    filtered_bets = {
        'available': [],
        'placed': []
    }

    for bet in bets:
        if user_can_place_bet(user, bet):
            filtered_bets['available'].append(bet)
        else:
            filtered_bets['placed'].append(get_placed_bet_for_profile(profile=user.profile, bet=bet))

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
    from django.contrib.auth.models import User
    from .models import ChoiceBet, DateBet

    assert isinstance(user, User)

    index = {}

    choice_bets = filter_visible_bets(user=user, bets=ChoiceBet.objects.all())
    index['choice_bets'] = filter_index_bets(user=user, bets=choice_bets)

    date_bets = filter_visible_bets(user=user, bets=DateBet.objects.all())
    index['date_bets'] = filter_index_bets(user=user, bets=date_bets)

    return index


def generate_profile_resolved_bet(profile):
    """
    Generates the data for resolved bets for user profile page
    :param profile: The Profile
    :return: A dictionary of the form:
    {
        'resolved_placed_choice_bets': [resolved ChoiceBet],
        'resolved_placed_date_bets': [resolved DateBet]
    }
    """
    from profiles.models import Profile
    from .models import PlacedChoiceBet, PlacedDateBet

    assert isinstance(profile, Profile)

    resolved_bets = {
        'resolved_placed_choice_bets': PlacedChoiceBet.objects.filter(placed_by=profile, placed_on__resolved=True),
        'resolved_placed_date_bets': PlacedDateBet.objects.filter(placed_by=profile, placed_on__resolved=True)
    }

    return resolved_bets


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

    assert isinstance(profile, Profile)
    assert isinstance(bet, Bet)

    username = profile.user.username
    profile = profile.account
    description = "Placed Bet\nBet: " + str(bet.prim_key) + "\nUser: " + username + "\nAmount: " + str(amount)

    try:
        one_to_one_transaction(
            origin=profile,
            destination=bet.account,
            description=description,
            amount=amount
        )
    except InsufficientFunds:
        raise


def perform_payout(bet, winning_bets):
    """
    Pays out the pot of a bet to the winning users
    :param bet: A subtype of Bet
    :param winning_bets: list of winning placed bets
    :return: transaction detailing the payout (already saved)
    """
    from ledger.models import Account
    from ledger.util import one_to_many_transaction
    from ledger.exceptions import InsufficientFunds

    payout = int(bet.account.balance / len(winning_bets))

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
            'account': Account.objects.get(name='operator', type='o'),
            'amount': bet.account.balance % len(winning_bets)
        }
    )

    description = "Payout\nBet: " + str(bet.id)
    for winner in winners:
        description += "\nAccount: " + winner['account'].name + ", Amount: " + str(winner['amount'])

    try:
        transaction = one_to_many_transaction(origin=bet.account, destinations=winners, description=description)
    except InsufficientFunds:
        logger.error("The pot division fucked up...")
        raise InsufficientFunds("The pot division fucked up...", code='pot_division_error')

    return transaction


def resolve_bet(bet, winning_option):
    """
    Resolves a bet and performs the payout
    :param bet: Either a ChoiceBet or a DateBet
    :param winning_option: Either a Choice or datetime.date
    :return: transaction detailing the payout
    """
    from .models import DateBet, ChoiceBet, Choice
    from ledger.exceptions import InsufficientFunds
    from datetime import date

    assert isinstance(bet, DateBet) or isinstance(bet, ChoiceBet)

    if isinstance(bet, DateBet):
        assert isinstance(winning_option, date)
        bet.winning_date = winning_option
        placed_bets = bet.placeddatebet_set.all()
        winning_bets = find_winning_dates(placed_bets=placed_bets, winning_date=winning_option)
    elif isinstance(bet, ChoiceBet):
        assert isinstance(winning_option, Choice)
        bet.winning_choice = winning_option
        placed_bets = bet.placedchoicebet_set.all()
        winning_bets = find_winning_choices(placed_bets=placed_bets, winning_choice=winning_option)
    else:
        logger.warning("Tried to resolve bet (" + bet + ")with unknown bet type.")
        return None

    try:
        transaction = perform_payout(bet=bet, winning_bets=winning_bets)
    except InsufficientFunds:
        raise

    bet.resolved = True
    bet.save()

    return transaction


def find_winning_dates(placed_bets, winning_date):
    """
    Finds the placed bets with the dates closest to the winning date
    :param placed_bets: iterable of PlacedDateBet
    :param winning_date: datetime.date
    :return: list of winning PlacedDateBets
    """
    from datetime import date
    from .models import PlacedDateBet

    assert isinstance(winning_date, date)

    dates = []
    for placed_bet in placed_bets:
        assert isinstance(placed_bet, PlacedDateBet)
        dates.append(placed_bet.placed_date)

    timedeltas = []
    for date in dates:
        timedeltas.append(abs(winning_date - date))

    closest = min(timedeltas)

    indices = []
    for i in range(0, len(timedeltas)):
        if timedeltas[i] == closest:
            indices.append(i)

    winning_bets = []
    for index in indices:
        winning_bets.append(placed_bets[index])

    return winning_bets


def find_winning_choices(placed_bets, winning_choice):
    """
    Finds the placed bets with the correct choice chosen
    :param placed_bets: iterable of PlacedChoiceBet
    :param winning_choice: Choice
    :return: list of winning PlacedChoiceBets
    """
    from .models import Choice, PlacedChoiceBet

    assert isinstance(winning_choice, Choice)

    winning_bets = []

    for placed_bet in placed_bets:
        assert isinstance(placed_bet, PlacedChoiceBet)
        if placed_bet.chosen == winning_choice:
            winning_bets.append(placed_bet)

    return winning_bets


def create_choices(request, bet):
    """
    Creates choices from ChoiceBet creation form.
    :param request: Request of the creation page. Is necessary to get POST data.
    :param bet: Bet to create choices for
    """
    from .models import Choice

    last_choice = False
    choice_number = 1
    choices = []
    choice_descriptions = []

    while not last_choice:
        description = request.POST.get("choice_" + str(choice_number))
        if description is not None:
            if description != "" and description not in choice_descriptions:
                choice_descriptions.append(description)
                choices.append(
                    Choice(
                        belongs_to=bet,
                        description=description
                    )
                )
                choice_number += 1
            else:
                raise ValidationError("Invalid choice descriptions", code='invalid_choice_descriptions')
        else:
            last_choice = True

    for choice in choices:
        choice.save()
