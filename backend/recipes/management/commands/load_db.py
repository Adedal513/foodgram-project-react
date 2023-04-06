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

DUMMY_USER_DATA = {
    'username': 'Ivan123',
    'first_name': 'Иван',
    'last_name': 'Иванов',
    'password': '123qwe',
    'email': 'ivan@mail.com'
}


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
            User.objects.create_user(**DUMMY_USER_DATA)
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
