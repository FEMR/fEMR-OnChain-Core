# Generated by Django 3.2.12 on 2022-03-03 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_rename_strenth_unit_inventoryentry_strength_unit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="treatment",
            name="medication",
            field=models.ManyToManyField(blank=True, to="main.InventoryEntry"),
        ),
    ]