def sum_credit_debit(credit, debit):
    """
    Calculates the total of the transactions
    :param credit: Credits
    :param debit: Debits
    :return:
    """
    credit_sum = 0

    for credit in credit:
        credit_sum += credit.amount

    debit_sum = 0

    for debit in debit:
        debit_sum += debit.amount

    return credit_sum - debit_sum


def create_table(credit, debit):
    """
    Brings the transactions in a form which can be displayed as a table.
    :param credit: Credits
    :param debit: Debits
    :return:
    """
    table = []

    for entry in credit:
        table.append((entry.transaction.timestamp, entry.amount, "-"))
    for entry in debit:
        table.append((entry.transaction.timestamp, "-", entry.amount))

    return sorted(table, key=lambda x: x[0])


def place_bet_transaction(user, bet, amount):
    """
    Creates and saves a transaction to transfer money when a bet is placed
    :param user: user that placed the bet
    :param bet: well... the bet
    :param amount: the amount that was placed
    :return: Transaction-object
    """
    from django.utils.translation import ugettext_lazy as _
    from django.contrib.auth.models import User

    from .models import Transaction, Debit, Credit
    from .exceptions import InsufficientFunds
    from bets.models import Bet
    from profiles.models import Profile

    assert isinstance(user, User) or isinstance(user, Profile)
    if isinstance(user, User):
        username = user.username
        user = user.profile.account
    else:
        username = user.user.username
        user = user.account

    assert isinstance(bet, Bet)
    bet_id = bet.id
    bet = bet.account

    if not user.balance >= amount:
        raise InsufficientFunds(
            _("User has insufficient funds"),
            code='insufficient_funds_on_placement'
        )

    transaction = Transaction(
        description="Placed Bet\nBet: " + str(bet_id) + "\nUser: " + username + "\nAmount: " + str(amount)
    )
    debit = Debit(
        transaction=transaction,
        account=user,
        amount=amount
    )
    credit = Credit(
        transaction=transaction,
        account=bet,
        amount=amount
    )

    transaction.save()
    debit.save()
    credit.save()

    user.compute_balance()
    bet.compute_balance()

    return transaction

