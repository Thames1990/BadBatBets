import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import ChoiceBet, DateBet
from ...util import resolve_bet
from bets.exceptions import NoPlacedBets


class Command(BaseCommand):
    help = 'Checks all bets, marks them as resolved if required and distributes the pot'

    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        for choice_bet in ChoiceBet.objects.all():
            if choice_bet.end_date:
                if choice_bet.end_date >= timezone.now().date():
                    try:
                        resolve_bet(choice_bet, None)
                        logging.info(choice_bet.name + " was automatically resolved. All participants regained their "
                                                       "placed points.")
                    except NoPlacedBets:
                        logging.warning(choice_bet.name + " couldn't be automatically resolved, because noone has "
                                                          "placed a bet yet. ")

        for date_bet in DateBet.objects.all():
            if date_bet.time_period_end:
                if date_bet.time_period_end >= timezone.now().date():
                    try:
                        resolve_bet(date_bet, date_bet.time_period_end)
                        logging.info(date_bet.name + " was automatically resolved.")
                    except NoPlacedBets:
                        logging.warning(date_bet.name + " couldn't be automatically resolved, because noone has "
                                                        "placed a bet yet. ")
