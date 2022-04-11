# Generated by Django 3.2.12 on 2022-03-22 17:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0010_alter_patient_date_of_birth"),
    ]

    operations = [
        migrations.AlterField(
            model_name="patient",
            name="age",
            field=models.PositiveIntegerField(
                validators=[
                    django.core.validators.MaxValueValidator(120),
                    django.core.validators.MinValueValidator(0),
                ]
            ),
        ),
    ]