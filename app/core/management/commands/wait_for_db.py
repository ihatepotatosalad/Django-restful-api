"""DJANGO COMMAND TO WAIT FOR DB TO BE AVALIBLE"""
import time
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError


class Command(BaseCommand):
    """COMMAND TO WAIT FOR DJANGOP TO WAIT FOR DATABASE"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for Database')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write(
                    'database unavalible, waiting 1 second...'
                )
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('DATABASE AVALIBLE'))
