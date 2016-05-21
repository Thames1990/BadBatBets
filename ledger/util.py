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
