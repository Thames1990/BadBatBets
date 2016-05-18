def sum_credit_debit(credits, debits):
    credit_sum = 0

    for credit in credits:
        credit_sum += credit.amount

    debit_sum = 0

    for debit in debits:
        debit_sum += debit.amount

    return credit_sum - debit_sum
