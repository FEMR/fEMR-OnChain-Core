# Generated by Django 3.1.7 on 2021-04-29 01:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_auto_20210428_2054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patientencounter',
            name='treatments',
        ),
        migrations.AddField(
            model_name='treatment',
            name='diagnosis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.diagnosis'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='encounter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.patientencounter'),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='prescriber',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
