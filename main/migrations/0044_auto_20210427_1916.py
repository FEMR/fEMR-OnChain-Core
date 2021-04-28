# Generated by Django 3.1.7 on 2021-04-27 23:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_auto_20210424_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='treatment',
            name='prescriber',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='InventoryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume', models.IntegerField()),
                ('medication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.medication')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entries', models.ManyToManyField(to='main.InventoryEntry')),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.inventory'),
        ),
    ]
