# Generated by Django 3.1.7 on 2021-04-29 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20210427_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treatment',
            name='administration_schedule',
            field=models.CharField(choices=[], max_length=8),
        ),
        migrations.DeleteModel(
            name='AdministrationSchedule',
        ),
    ]
