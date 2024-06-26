# Generated by Django 5.0.6 on 2024-05-14 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_alter_order_problem_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="building",
            field=models.CharField(
                choices=[
                    ("main", "Главный"),
                    ("baizak", "Байзак"),
                    ("gym", "Спортзал"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("submitted", "Submitted"),
                    ("accepted", "Accepted"),
                    ("in_progress", "In Progress"),
                    ("completed", "Completed"),
                ],
                default="submitted",
                max_length=20,
            ),
        ),
    ]
