"""
Classes defining characteristics for data entry forms.
Forms are generated as HTML from the structure of each Form's superclass.
"""
import math

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from django.forms import ModelForm, Form, CharField, PasswordInput, DateInput, ValidationError, BooleanField
from django.forms.models import ModelMultipleChoiceField
from django.forms.widgets import Textarea
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, MultiField

from .models import Patient, PatientEncounter, fEMRUser, Campaign, Instance, Contact, Vitals,\
    ChiefComplaint, Treatment, Diagnosis, Medication, AdministrationSchedule


class ChiefComplaintForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = ChiefComplaint
        fields = '__all__'
        labels = {
            'text': 'Chief Complaint',
        }


class DiagnosisForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Diagnosis
        fields = '__all__'
        labels = {
            'text': 'Diagnosis'
        }


class MedicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Medication
        fields = '__all__'
        labels = {
            'text': 'Medication'
        }


class AdministrationScheduleForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = AdministrationSchedule
        fields = '__all__'
        labels = {
            'text': 'Administration Schedule'
        }


class TreatmentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            MultiField(
                Div('medication'),
                Div('administration_schedule'),
                Div('days'),
            ),
        )

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Treatment
        fields = '__all__'


class DateInputOverride(DateInput):
    """
    Overrides the form type for date inputs.
    """
    input_type = 'date'


class RegisterForm(Form):
    """
    Handles managing forms for new user registration.
    """
    username = CharField(label="Username", max_length=100)
    password = CharField(label="Password", widget=PasswordInput)
    password_conf = CharField(label="Confirm Password", widget=PasswordInput)
    first = CharField(label="First Name", max_length=100)
    last = CharField(label="Last Name", max_length=100)
    email = CharField(label="Email Address", max_length=100)


class LoginForm(Form):
    """
    Handles managing forms for user authentication.
    """
    username = CharField(label="Username", max_length=100)
    password = CharField(label="Password", widget=PasswordInput)
    remember_me = BooleanField(required=False)


class PatientForm(ModelForm):
    """
    Data entry form - Patient
    """

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].widget.attrs['max'] = "9999-12-31"
        self.fields['date_of_birth'].widget.attrs['maxlength'] = "6"
        self.fields['date_of_birth'].widget.attrs[
            'pattern'] = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4}$"
        self.fields['phone_number'].widget.attrs['required'] = False
        self.fields['email_address'].widget.attrs['required'] = False
        self.fields['social_security_number'].widget.attrs['minlength'] = "4"
        self.fields['zip_code'].widget.attrs['minlength'] = "5"
        self.fields['age'].widget.attrs['style'] = "pointer-events: none; -webkit-appearance: none; margin: 0; -moz-appearance:textfield;"
        self.fields['age'].widget.attrs['readonly'] = ""

    def clean_social_security_number(self):
        if self.cleaned_data['social_security_number'] is None:
            return self.cleaned_data['social_security_number']
        if len(self.cleaned_data['social_security_number'].replace(
            '-', '').replace('_', '')) != 4 and len(self.cleaned_data['social_security_number'].replace(
                '-', '').replace('_', '')) != 9:
            raise ValidationError('Must be 4 or 9 digits.')
        return self.cleaned_data['social_security_number']

    def clean_zip_code(self):
        if self.cleaned_data['zip_code'] is None:
            return self.cleaned_data['zip_code']
        if len(self.cleaned_data['zip_code'].replace(
            '-', '').replace('_', '')) != 5 and len(self.cleaned_data['zip_code'].replace(
                '-', '').replace('_', '')) != 9:
            raise ValidationError('Must be 5 or 9 digits.')
        return self.cleaned_data['zip_code']

    def clean_date_of_birth(self):
        if self.cleaned_data['date_of_birth'] > timezone.now().date():
            raise ValidationError('Must not be later than today.')
        return self.cleaned_data['date_of_birth']

    def clean_phone_number(self):
        if self.cleaned_data['phone_number'] is None:
            pass
        elif 'shared_phone_number' not in self.data.keys():
            p = Patient.objects.filter(
                phone_number=self.cleaned_data['phone_number'])
            if p.exists() and len(p) != 1 and self.instance not in p:
                raise ValidationError(
                    'This phone number has already been used.')
        return self.cleaned_data['phone_number']

    def clean_email_address(self):
        if self.cleaned_data['email_address'] is None:
            pass
        elif 'shared_email_address' not in self.data.keys():
            p = Patient.objects.filter(
                email_address=self.cleaned_data['email_address'])
            if p.exists() and len(p) != 1 and self.instance not in p:
                raise ValidationError(
                    'This email address has already been used.')
        return self.cleaned_data['email_address']

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Patient
        fields = '__all__'
        exclude = ('campaign',)
        labels = {
            'phone_number': 'Phone number',
            'email_address': 'Email address'
        }
        widgets = {
            'date_of_birth': DateInputOverride(attrs={
                'pattern': "^[0-9]{2}\/[0-9]{2}\/[0-9]{4}$",
                'placeholder': "dd/mm/yyyy"
            })
        }


class PatientEncounterForm(ModelForm):
    """
    Data entry form - PatientEncounter
    """

    def __init__(self, *args, **kwargs):
        self.unit = kwargs.pop('unit', None)
        super(PatientEncounterForm, self).__init__(*args, **kwargs)
        self.fields['body_height_primary'].widget.attrs['min'] = 0
        self.fields['body_height_primary'].widget.attrs['max'] = 10
        self.fields['body_height_secondary'].widget.attrs['min'] = 0
        self.fields['body_height_secondary'].widget.attrs['step'] = .01
        self.fields['body_height_secondary'].widget.attrs['maxlength'] = 4
        self.fields['body_height_secondary'].widget.attrs[
            'pattern'] = "^[0-9]{0,2}[\.]{0,1}[0-9]{0,2}$"
        self.fields['body_height_secondary'].widget.attrs['value'] = 0.00
        self.fields['body_mass_index'].widget.attrs['step'] = .1
        self.fields['bmi_percentile'].widget.attrs['min'] = 0
        self.fields['body_mass_index'].widget.attrs['min'] = 0
        self.fields['body_mass_index'].widget.attrs['style'] = "pointer-events: none; -webkit-appearance: none; margin: 0; -moz-appearance:textfield;"
        self.fields['body_mass_index'].widget.attrs['readonly'] = ""
        self.fields['weeks_pregnant'].widget.attrs['min'] = 0
        self.fields['weeks_pregnant'].widget.attrs['max'] = 45
        if self.unit == 'i':
            self.fields['body_weight'].label = 'Body weight - Pounds'
            self.fields['body_height_primary'].label = 'Height - Feet'
            self.fields['body_height_primary'].widget.attrs['max'] = 9
            self.fields['body_height_secondary'].label = 'Height - Inches'
            self.fields['body_height_secondary'].widget.attrs['max'] = 11.9
            self.fields['body_weight'].widget.attrs['min'] = 5
        else:
            self.fields['body_weight'].label = 'Body weight - Kilos'
            self.fields['body_height_primary'].label = 'Height - Meters'
            self.fields['body_height_primary'].widget.attrs['max'] = 3
            self.fields['body_height_secondary'].label = 'Height - Centimeters'
            self.fields['body_height_secondary'].widget.attrs['max'] = 100
            self.fields['body_weight'].widget.attrs['min'] = 0.25

    def clean_body_mass_index(self):
        if self.cleaned_data['body_mass_index'] < 5:
            self.add_error('body_height_primary',
                           "BMI shouldn't be less than 5%. Check these numbers.")
            self.add_error(
                'body_weight', "BMI shouldn't be less than 5%. Check these numbers.")
        return self.cleaned_data['body_mass_index']

    def save(self, commit=True):
        m = super(PatientEncounterForm, self).save(commit=False)
        if self.unit == 'i':
            tmp = m.body_height_primary
            m.body_height_primary = math.floor(
                (((m.body_height_primary * 12) + m.body_height_secondary) * 2.54) // 100)
            m.body_height_secondary = (
                ((tmp * 12) + m.body_height_secondary) * 2.54) % 100
            m.body_weight = m.body_weight / 2.2046
        if commit:
            m.save()
        return m

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = PatientEncounter
        fields = '__all__'
        labels = {
            'body_mass_index': 'Body Mass Index',
        }
        widgets = {
            # 'diagnoses': AutoCompleteSelectMultipleWidget(DiagnosisLookup),
            # 'treatments': AutoCompleteSelectMultipleWidget(TreatmentLookup),
            # 'chief_complaint': AutoCompleteSelectMultipleWidget(ChiefComplaintLookup),
            'patient_history': Textarea(attrs={'rows': 4, 'cols': 40}),
            'community_health_worker_notes': Textarea(attrs={'rows': 4, 'cols': 40})
        }


class VitalsForm(ModelForm):
    """
    Data entry form - Vitals
    """

    def __init__(self, *args, **kwargs):
        self.unit = kwargs.pop('unit', None)
        super(VitalsForm, self).__init__(*args, **kwargs)
        self.fields['diastolic_blood_pressure'].widget.attrs['min'] = 0
        self.fields['systolic_blood_pressure'].widget.attrs['min'] = 0
        self.fields['oxygen_concentration'].widget.attrs['min'] = 70
        self.fields['oxygen_concentration'].widget.attrs['max'] = 100
        self.fields['heart_rate'].widget.attrs['min'] = 40
        self.fields['heart_rate'].widget.attrs['max'] = 170
        self.fields['respiratory_rate'].widget.attrs['min'] = 0
        self.fields['body_temperature'].widget.attrs['step'] = 0.01
        self.fields['mean_arterial_pressure'].widget.attrs['style'] = "pointer-events: none; -webkit-appearance: none; margin: 0; -moz-appearance:textfield;"
        self.fields['mean_arterial_pressure'].widget.attrs['readonly'] = ""
        self.fields['glucose_level'].widget.attrs['min'] = 0
        if self.unit == 'i':
            self.fields['body_temperature'].label = 'Body temperature - Fahrenheit'
            self.fields['body_temperature'].widget.attrs['min'] = 93
            self.fields['body_temperature'].widget.attrs['max'] = 113
        else:
            self.fields['body_temperature'].label = 'Body temperature - Celsius'
            self.fields['body_temperature'].widget.attrs['min'] = 34
            self.fields['body_temperature'].widget.attrs['max'] = 45

    def clean_body_mass_index(self):
        if self.cleaned_data['body_mass_index'] < 5:
            self.add_error('body_height_primary',
                           "BMI shouldn't be less than 5%. Check these numbers.")
            self.add_error(
                'body_weight', "BMI shouldn't be less than 5%. Check these numbers.")
        return self.cleaned_data['body_mass_index']

    def save(self, commit=True):
        m = super(VitalsForm, self).save(commit=False)
        if self.unit == 'i':
            m.body_temperature = (m.body_temperature - 32) * (5/9)
        if commit:
            m.save()
        return m

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Vitals
        fields = '__all__'
        labels = {
            'mean_arterial_pressure': 'Mean Arterial Pressure',
            'smoking': 'Tobacco Use Disorder',
            'alcohol': 'History of Substance/Alcohol Abuse',
        }


class UserForm(UserCreationForm):
    """
    Data entry form - fEMRUser
    """
    groups = ModelMultipleChoiceField(queryset=Group.objects.exclude(
        name="fEMR Admin").exclude(name="Manager"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = fEMRUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
            'groups'
        ]


class fEMRAdminUserForm(UserCreationForm):
    """
    Data entry form - fEMRUser
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = fEMRUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
            'groups',
            'campaigns'
        ]


def filter_campaigns_for_instances(user):
    campaigns = user.campaigns.all()
    instances = [c.instance for c in campaigns]
    return Campaign.objects.filter(instance__in=instances)


class UserUpdateForm(UserChangeForm):
    """
    Data entry form - fEMRUser
    """
    password = None
    groups = ModelMultipleChoiceField(queryset=Group.objects.exclude(
        name="fEMR Admin").exclude(name="Manager"), required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['campaigns'].queryset = filter_campaigns_for_instances(
            user)

    class Meta:
        model = fEMRUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'campaigns',
            'groups',
        ]


class fEMRAdminUserUpdateForm(UserChangeForm):
    """
    Data entry form - fEMRUser
    """
    password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = fEMRUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'groups',
            'campaigns'
        ]


class AdminPasswordForm(UserCreationForm):
    """
    Data entry form - fEMRUser
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = fEMRUser
        fields = [
            'password1',
            'password2'
        ]


class InstanceForm(ModelForm):
    """
    Data entry form - Instance
    """

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Instance
        fields = '__all__'


class CampaignForm(ModelForm):
    """
    Data entry form - Campaign
    """

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Campaign
        fields = '__all__'


class ContactForm(ModelForm):
    """
    Data entry form - Contact
    """

    class Meta:
        """
        Metaclass controlling model references.
        """
        model = Contact
        fields = '__all__'


class ForgotUsernameForm(Form):
    email = CharField(label="Email address", max_length=256)
