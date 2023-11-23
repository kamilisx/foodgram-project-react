import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from recipes.models import Ingredient

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            csv_to_db(Ingredient, "ingredients.csv")
        except IntegrityError as error:
            raise CommandError(error)

        self.stdout.write(self.style.SUCCESS("Successfully written to db"))


def csv_to_db(model, filename):
    file_path = os.path.abspath(f"data/{filename}")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in csv.reader(f):
            model.objects.get_or_create(name=line[0], measurement_unit=line[1])
