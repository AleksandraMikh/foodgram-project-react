import os
import csv
from django.core.management.base import BaseCommand
from foodgram_project.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    def fill_models_without_foreign_keys(self):
        with open(os.path.join(
                BASE_DIR, 'static_backend/data/ingredients.csv')) as csvfile:
            fieldnames = ['name', 'measurement_unit']
            reader = csv.DictReader(csvfile, fieldnames)
            result = []
            for row in reader:
                i = Ingredient(
                    name=row['name'], measurement_unit=row['measurement_unit'])
                result.append(i)
            Ingredient.objects.bulk_create(
                result, ignore_conflicts=True)

    def handle(self, *args, **options):
        self.fill_models_without_foreign_keys()
        self.stdout.write(self.style.SUCCESS(
            'SUCCESS: import ingredients.csv'))
