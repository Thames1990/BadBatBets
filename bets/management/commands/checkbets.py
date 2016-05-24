import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import ChoiceBet, DateBet


class Command(BaseCommand):
    help = 'Checks all bets, marks them as resolved if required and distributes the pot'

    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        choice_bets = ChoiceBet.objects.all()
        for choice_bet in choice_bets:
            if choice_bet.end_date:
                if choice_bet.end_date >= timezone.now().date():
                    choice_bet.resolved = True
                    # TODO distribution of the pot (placedchoicebet_set)
                    choice_bet.save()
                    logging.info(choice_bet.name + " is now resolved")

        date_bets = DateBet.objects.all()
        for date_bet in date_bets:
            if date_bet.time_period_end:
                if date_bet.time_period_end >= timezone.now().date():
                    date_bet.resolved = True
                    # TODO distribution of the pot (placeddatebet_set)
                    date_bet.save()
                    logging.info(date_bet.name + " is now resolved")
