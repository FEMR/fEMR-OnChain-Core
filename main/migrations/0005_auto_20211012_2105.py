# Generated by Django 3.2.8 on 2021-10-13 01:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0004_alter_campaign_encounter_close'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersession',
            name='session',
        ),
        migrations.AddField(
            model_name='usersession',
            name='session_key',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='usersession',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='usersession',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='logged_in_user',
                                       to=settings.AUTH_USER_MODEL),
        ),
    ]