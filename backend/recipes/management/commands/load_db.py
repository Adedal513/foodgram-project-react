import csv
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import models
from recipes.models import Ingredient, Tag

User = get_user_model()

MODELS_SOURCE = [
    ('recipes/data/ingredients.csv', Ingredient),
    ('recipes/data/tags.csv', Tag)
]

USER_SOURCE = ('recipes/data/users.csv', User)


class Command(BaseCommand):
    help = 'Наполняет БД тегами и ингредиентами.'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '-u',
            '--dummy_user',
            action='store_true',
            help='Создание тестового пользователя'
        )

    def handle(self, *args: Any, **options: Any) -> str | None:

        for path, model in MODELS_SOURCE:
            self._populate_model(path, model)

        if options['dummy_user']:
            path, model = USER_SOURCE
            self._populate_model(path, model, True)

        self.stdout.write(self.style.SUCCESS('DB successfully populated'))

    def _populate_model(self,
                        source: str,
                        model: models.Model,
                        user_mode: bool | None = False):
        with open(source, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    if user_mode:
                        model.objects.create_user(**row)
                    else:
                        model.objects.create(**row)
                except Exception as e:
                    raise CommandError(
                        f'Error while populating model {model}: {e}'
                    )
