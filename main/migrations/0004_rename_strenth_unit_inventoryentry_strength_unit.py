# Generated by Django 3.2.10 on 2022-03-01 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_auto_20220223_1227"),
    ]

    operations = [
        migrations.RenameField(
            model_name="inventoryentry",
            old_name="strenth_unit",
            new_name="strength_unit",
        ),
    ]
