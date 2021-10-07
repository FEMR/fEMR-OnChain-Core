from django.db import migrations, models


race_choices = (
    ('1', 'Native American or Native Alaskan'),
    ('2', 'Asian'),
    ('3', 'Black, African American'),
    ('4', 'Hispanic or Latinx'),
    ('5', 'Mixed Race'),
    ('6', 'White'),
    ('7', 'Nondisclosed'),
)

ethnicity_choices = (
    ('1', 'Hispanic or Latinx'),
    ('2', 'Not Hispanic or Latinx'),
    ('3', 'Nondisclosed'),
)


def race_and_ethnicity_data_migrate(apps, schema_editor):
    Patient = apps.get_model("main", "Patient")
    Race = apps.get_model("main", "Race")
    Ethnicity = apps.get_model("main", "Ethnicity")
    for p in Patient.objects.all():
        if p.race is None and p.race_text is not None:
            p.race = Race.objects.get_or_create(name=race_choices[p.race_text])[0]
            p.save()
        if p.ethnicity is None and p.ethnicity_text is not None:
            p.ethnicity = Ethnicity.objects.get_or_create(name=ethnicity_choices[p.ethnicity_text])[0]
            p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0089_auto_20210901_0100'),
    ]

    operations = [
        migrations.RunPython(race_and_ethnicity_data_migrate),
    ]
