import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from recipes.models import Ingredient

User = get_user_model()


class Command(BaseCommand):
    """Custom command for reading csv file and saving data to database."""
    help: str = (
        'Read csv files in "static/data" folder and write them to database',
    )

    def handle(self, *args, **options) -> None:
        """Try to csv_to_db and stdout success text.

        Raise exception if false.
        """
        try:
            csv_to_db(Ingredient, "ingredients.csv")
        except IntegrityError as error:
            raise CommandError(error)

        self.stdout.write(self.style.SUCCESS("Successfully write to db"))


def csv_to_db(model: Ingredient, filename: str) -> None:
    """Read a csv file and create a new entry in database."""
    file_path: str = os.path.abspath(f"data/{filename}")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in csv.reader(f):
            model.objects.get_or_create(name=line[0], measurement_unit=line[1])
