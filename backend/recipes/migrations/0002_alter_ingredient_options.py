# Generated by Django 4.1.7 on 2023-03-23 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ingredient",
            options={
                "ordering": ["name"],
                "verbose_name": "Ингрeдиент",
                "verbose_name_plural": "Ингрeдиенты",
            },
        ),
    ]
