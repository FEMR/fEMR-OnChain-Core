# Generated by Django 3.1.1 on 2020-11-21 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20201121_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='campaign',
            field=models.ManyToManyField(default=1, to='main.Campaign'),
        ),
    ]
