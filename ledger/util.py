def sum_credit_debit(cre, deb):
    """
    Calculates the total of the transactions
    :param cre: Credits
    :param deb: Debits
    :return:
    """
    credit_sum = 0

    for credit in cre:
        credit_sum += credit.amount

    debit_sum = 0

    for debit in deb:
        debit_sum += debit.amount

    return credit_sum - debit_sum


def create_table(cre, deb):
    """
    Brings the transactions in a form which can be displayed as a table.
    :param cre: Credits
    :param deb: Debits
    :return:
    """
    table = []

    for entry in cre:
        table.append((entry.transaction.timestamp, entry.amount, "-"))
    for entry in deb:
        table.append((entry.transaction.timestamp, "-", entry.amount))

    return sorted(table, key=lambda x: x[0])
