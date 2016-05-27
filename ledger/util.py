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
    :param amount: Amount to be transfered
    :return: Transaction-object
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
    debit = Debit(
        transaction=transaction,
        account=origin,
        amount=amount
    )
    credit = Credit(
        transaction=transaction,
        account=destination,
        amount=amount
    )

    transaction.save()
    debit.save()
    credit.save()

    origin.compute_balance()
    destination.compute_balance()

    return transaction

