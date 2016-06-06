def sum_credit_debit(credit, debit):
    """
    Calculates the total of the transactions
    :param credit: Credits
    :param debit: Debits
    :return:
    """
    credit_sum = 0
    for entry in credit:
        credit_sum += entry.amount

    debit_sum = 0
    for entry in debit:
        debit_sum += entry.amount

    return credit_sum - debit_sum


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

    transaction = Transaction.objects.create(description=description)

    Debit.objects.create(
        transaction=transaction,
        account=origin,
        amount=amount
    )

    Credit.objects.create(
        transaction=transaction,
        account=destination,
        amount=amount
    )

    origin.compute_balance()
    destination.compute_balance()


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

    transaction = Transaction.objects.create(description=description)

    # TODO Specify all parameters for all functions everywhere? (convention)
    Debit.objects.create(
        transaction=transaction,
        account=origin,
        amount=total_amount
    )
    origin.compute_balance()

    for destination in destinations:
        Credit.objects.create(
            transaction=transaction,
            account=destination['account'],
            amount=destination['amount']
        )
        destination['account'].compute_balance()
