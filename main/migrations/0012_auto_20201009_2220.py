# Generated by Django 3.1.1 on 2020-10-10 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20201009_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='instance',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
