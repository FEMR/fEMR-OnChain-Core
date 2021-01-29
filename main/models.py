"""
Enumerates all contents of all database models.
Migrations run will generate a table for each of these containing the listed fields.
"""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.validators import BaseValidator, MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from localflavor.us.models import USStateField
from rest_framework.authtoken.models import Token
from timezone_utils.choices import COMMON_TIMEZONES_CHOICES

birth_sex_choices = (('f', 'Female'), ('m', 'Male'), ('o', 'Other'))
suffix_choices = (('j', 'Jr.'), ('s', 'Sr.'),
                  ('1', 'I'), ('2', 'II'), ('3', 'III'))
unit_choices = (('i', 'Imperial'), ('m', 'Metric'))
race_choices = (
    ('1', 'Native American or Native Alaskan'),
    ('2', 'Asian'),
    ('3', 'Black, African American'),
    ('4', 'Hispanic or Latinx'),
    ('5', 'White'),
    ('6', 'Nondisclosed'),
)
ethnicity_choices = (
    ('1', 'Hispanic or Latinx'),
    ('2', 'Not Hispanic or Latinx'),
    ('3', 'Nondisclosed'),
)


class Contact(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email_address = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)


class Instance(models.Model):
    name = models.CharField(max_length=30, unique=True)
    active = models.BooleanField(default=True)
    main_contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=30, unique=True)
    active = models.BooleanField(default=True)
    units = models.CharField(max_length=30, choices=unit_choices, default="m")
    timezone = models.CharField(
        max_length=100, choices=COMMON_TIMEZONES_CHOICES)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Patient(models.Model):
    """
    Used to manage data elements for the given patient.
    This may, in clinical settings, be a standalone object,
    or may be connected directly to a user of the fEMR-OnChain platform.
    """
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30)
    suffix = models.CharField(
        max_length=30, choices=suffix_choices, null=True, blank=True)

    social_security_number = models.CharField(
        max_length=11, unique=True, null=True, blank=True, validators=[MinLengthValidator(4)])
    sex_assigned_at_birth = models.CharField(
        max_length=6, choices=birth_sex_choices)
    explain = models.CharField(max_length=400, null=True, blank=True)
    date_of_birth = models.DateField()
    age = models.IntegerField()
    race = models.CharField(max_length=30, choices=race_choices)
    ethnicity = models.CharField(max_length=30, choices=ethnicity_choices)
    preferred_language = models.CharField(max_length=30, null=True, blank=True)

    current_address = models.CharField(max_length=30, null=True, blank=True)
    address1 = models.CharField(
        "Address line 1",
        max_length=1024, null=True, blank=True
    )

    address2 = models.CharField(
        "Address line 2",
        max_length=1024, null=True, blank=True
    )

    zip_code = models.CharField(
        "ZIP / Postal code", max_length=12, null=True, blank=True, validators=[MinLengthValidator(5)]
    )

    city = models.CharField(
        "City",
        max_length=1024, null=True, blank=True
    )

    state = USStateField(null=True, blank=True)

    previous_address = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(
        max_length=13, null=True, blank=True)
    phone_number_type = models.CharField(max_length=30, null=True, blank=True)
    shared_phone_number = models.BooleanField()
    email_address = models.CharField(
        max_length=40, null=True, blank=True)
    shared_email_address = models.BooleanField()

    timestamp = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False)

    campaign = models.ManyToManyField(Campaign, default=1)

    # allergies = models.ManyToManyField(Allergy)
    # immunizations = models.ManyToManyField(Immunization)
    # problems = models.ManyToManyField(Problem)
    # procedures = models.ManyToManyField(Procedure)
    # health_concerns = models.ManyToManyField(HealthConcern)
    # medications = models.ManyToManyField(Medication)

    def __str__(self):
        """
        Streamlines casting the object to a string.

        :return: "FirstName LastName" as a string.
        """
        suffix = self.get_suffix_display() if self.suffix is not None else ""
        return str(self.first_name) + " " + str(self.last_name) + " " + suffix


@deconstructible
class ModifiedMaxValueValidator(BaseValidator):
    message = _('Ensure this value is less than %(limit_value)s.')
    code = 'max_value'

    def compare(self, a, b):
        return a > b


class PatientEncounter(models.Model):
    """
    Individual data point in a patient's medical record.
    """
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True)

    smoking = models.BooleanField(default=False)
    history_of_diabetes = models.BooleanField(default=False)
    history_of_hypertension = models.BooleanField(default=False)
    history_of_high_cholesterol = models.BooleanField(default=False)
    alcohol = models.BooleanField(default=False)

    diastolic_blood_pressure = models.IntegerField(
        validators=[MaxValueValidator(200), MinValueValidator(1)])
    systolic_blood_pressure = models.IntegerField(
        validators=[MaxValueValidator(200), MinValueValidator(1)])
    mean_arterial_pressure = models.FloatField(
        validators=[MinValueValidator(1)])
    body_height_primary = models.IntegerField(
        validators=[MaxValueValidator(8), MinValueValidator(0)])
    body_height_secondary = models.FloatField(
        validators=[ModifiedMaxValueValidator(100), MinValueValidator(0)])
    body_weight = models.FloatField(
        validators=[MaxValueValidator(500), MinValueValidator(0.25)])
    heart_rate = models.IntegerField(
        validators=[MaxValueValidator(170), MinValueValidator(40)])
    respiratory_rate = models.IntegerField(
        validators=[MaxValueValidator(500), MinValueValidator(1)], null=True, blank=True)
    body_temperature = models.FloatField(
        validators=[MaxValueValidator(200), MinValueValidator(1)])
    oxygen_concentration = models.IntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(70)], null=True, blank=True)
    bmi_percentile = models.IntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(1)], null=True, blank=True)
    weight_for_length_percentile = models.IntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(1)], null=True, blank=True)
    head_occipital_frontal_circumference_percentile = models.IntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(1)], null=True, blank=True)
    body_mass_index = models.FloatField(
        validators=[MaxValueValidator(500), MinValueValidator(0)], null=True, blank=True)
    glucose_level = models.FloatField(
        validators=[MaxValueValidator(500), MinValueValidator(1)], null=True, blank=True)
    weeks_pregnant = models.IntegerField(
        validators=[MaxValueValidator(45), MinValueValidator(1)], null=True, blank=True)

    community_health_worker_notes = models.CharField(
        max_length=500, null=True, blank=True)

    timestamp = models.DateTimeField(
        auto_now=True, editable=False, null=False, blank=False)

    @property
    def unit_aware_primary_height(self, unit):
        pass

    @property
    def unit_aware_secondary_height(self, unit):
        pass

    @property
    def unit_aware_weight(self, unit):
        return self.body_weight if unit == "m" else (self.body_weight * 2.2046)

    @property
    def unit_aware_temperature(self, unit):
        return self.body_temperature if unit == "m" else (self.body_temperature * 1.8) + 32

    def __str__(self):
        """
        Displays patient encounters in a more readable way.
        """
        return str(self.patient)


class fEMRUser(AbstractUser):
    """
    Inherits from Django's AbstractUser, adding fEMR-OnChain-relevant fields to the objects.
    """
    email = models.EmailField(unique=True)
    change_password = models.BooleanField(default=True, editable=False)
    campaigns = models.ManyToManyField(Campaign)
    password_reset_last = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '{} {} {}'.format(self.first_name, self.last_name, self.email)


class UnitsSetting(SingletonModel):
    units = models.CharField(
        max_length=30, choices=unit_choices, default="i")


class AuditEntry(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, blank=True, null=True)

    def __unicode__(self):
        return '{0} - {1} - {2} - {3}'.format(self.action, self.username, self.ip, self.timestamp, self.campaign)

    def __str__(self):
        return '{0} - {1} - {2} - {3}'.format(self.action, self.username, self.ip, self.timestamp, self.campaign)


class DatabaseChangeLog(models.Model):
    action = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    instance = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    def __unicode__(self):
        return '{0} {1} {2} - by {3} at {4}, {5}'.format(self.action, self.model, self.instance, self.ip, self.username,
                                                         self.timestamp)

    def __str__(self):
        return '{0} {1} {2} - by {3} at {4}, {5}'.format(self.action, self.model, self.instance, self.ip, self.username,
                                                         self.timestamp)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    from main.femr_admin_views import get_client_ip
    ip = get_client_ip(request)
    campaign_list = request.user.campaigns.filter(active=True)
    if len(campaign_list) != 0:
        name = campaign_list[0].name
        campaign = Campaign.objects.get(name=name)
    else:
        campaign = None
    AuditEntry.objects.create(action='user_logged_in',
                                  ip=ip, username=user.username, campaign=campaign)


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    from main.femr_admin_views import get_client_ip
    ip = get_client_ip(request)
    try:
        campaign_list = request.user.campaigns.filter(active=True)
        if len(campaign_list) != 0:
            name = campaign_list[0].name
            campaign = Campaign.objects.get(name=name)
        else:
            campaign = None
        AuditEntry.objects.create(action='user_logged_out',
                                    ip=ip, username=user.username, campaign=campaign)
    except AttributeError:
        pass


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    A general-purpose, commonly-used function generating authentication tokens for the RESTful API.
    Like any other view, this is never called directly and should be handled by the URL conf for djangorestframework.

    :param sender: Origin of the request.
    :param instance: The user to generate a Token for.
    :param created: Used to determine if a Token already exists for the given user.
    :param kwargs: Should be empty.
    """
    if created:
        Token.objects.create(user=instance)
