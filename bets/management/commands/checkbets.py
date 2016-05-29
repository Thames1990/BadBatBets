import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import ChoiceBet, DateBet


class Command(BaseCommand):
    help = 'Checks all bets, marks them as resolved if required and distributes the pot'

    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        for choice_bet in ChoiceBet.objects.all():
            if choice_bet.end_date:
                if choice_bet.end_date >= timezone.now().date():
                    choice_bet.resolved = True
                    choice_bet.save()
                    logging.info(choice_bet.name + " is now resolved")
                    # TODO Distribute pot

        for date_bet in DateBet.objects.all():
            if date_bet.time_period_end:
                if date_bet.time_period_end >= timezone.now().date():
                    date_bet.resolved = True
                    date_bet.save()
                    logging.info(date_bet.name + " is now resolved")
                    # TODO Distribute pot
