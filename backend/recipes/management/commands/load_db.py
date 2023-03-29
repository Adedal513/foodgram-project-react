import csv
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import models
from recipes.models import Ingredient, Tag

MODELS_SOURCE = [
    ('recipes/data/ingredients.csv', Ingredient),
    ('recipes/data/tags.csv', Tag)
]


class Command(BaseCommand):
    help = 'Наполняет БД тегами и ингредиентами.'

    def handle(self, *args: Any, **options: Any) -> str | None:
        for path, model in MODELS_SOURCE:
            self._populate_model(path, model)

        self.stdout.write(self.style.SUCCESS('DB successfully populated'))

    def _populate_model(self, source: str, model: models.Model):
        with open(source, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    model.objects.create(**row)
                except Exception as e:
                    raise CommandError(
                        f'Error while populating model {model}: {e}'
                    )
