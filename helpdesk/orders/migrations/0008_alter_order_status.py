# Generated by Django 5.0.6 on 2024-05-23 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0007_problem_department"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("submitted", "Отправлено"),
                    ("accepted", "Принято"),
                    ("in_progress", "В процессе"),
                    ("completed", "Завершено"),
                ],
                default="submitted",
                max_length=20,
            ),
        ),
    ]
