# Generated by Django 5.0.6 on 2024-05-14 05:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_problem_alter_order_building"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="problem_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="orders.problem",
            ),
        ),
    ]
