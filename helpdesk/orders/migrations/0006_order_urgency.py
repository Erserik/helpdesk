# Generated by Django 5.0.6 on 2024-05-23 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_alter_order_building_alter_order_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="urgency",
            field=models.CharField(
                choices=[
                    ("urgent", "Срочно"),
                    ("not_urgent", "Не срочно"),
                    ("very_urgent", "Очень срочно"),
                ],
                default="not_urgent",
                max_length=20,
            ),
        ),
    ]
