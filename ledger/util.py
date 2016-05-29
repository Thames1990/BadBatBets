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


def one_to_one_transaction(origin, destination, description, amount):
    """
    Creates a transaction with a single origin and destination
    :param origin: Account from which the money will be deducted
    :param destination: Account to which the money will be credited
    :param description: Description of the transaction
    :param amount: Amount to be transferred
    """
    from .models import Account, Transaction, Debit, Credit
    from .exceptions import InsufficientFunds

    assert isinstance(origin, Account)
    assert isinstance(destination, Account)
    assert isinstance(description, str)
    assert isinstance(amount, int)

    if origin.balance < amount:
        raise InsufficientFunds()

    transaction = Transaction(description=description)
    transaction.save()

    Debit(
        transaction=transaction,
        account=origin,
        amount=amount
    ).save()

    Credit(
        transaction=transaction,
        account=destination,
        amount=amount
    ).save()

    origin.compute_balance()
    destination.compute_balance()

    return transaction


def one_to_many_transaction(origin, destinations, description):
    """
    Creates a transaction with a single origin and many destinations
    :param origin: Account from which the money will be deducted
    :param destinations: Dictionary of the account and amount for each destination
    :param description: Description of the transaction
    """
    from .models import Account, Transaction, Debit, Credit
    from .exceptions import InsufficientFunds

    assert isinstance(origin, Account)
    assert isinstance(description, str)
    for destination in destinations:
        assert isinstance(destination['account'], Account)
        assert isinstance(destination['amount'], int)

    total_amount = 0
    for destination in destinations:
        total_amount += destination['amount']

    if origin.balance < total_amount:
        raise InsufficientFunds()

    transaction = Transaction(description=description)
    transaction.save()

    Debit(
        transaction=transaction,
        account=origin,
        amount=total_amount
    ).save()
    origin.compute_balance()

    for destination in destinations:
        Credit(
            transaction=transaction,
            account=destination['account'],
            amount=destination['amount']
        ).save()
        destination['account'].compute_balance()
