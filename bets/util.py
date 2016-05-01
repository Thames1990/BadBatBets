def pkgen():
    from random import SystemRandom

    randomiser = SystemRandom()
    # 2147483647 is the largest values supported by django's PositiveIntegerField
    return randomiser.randint(0, 2147483647)
