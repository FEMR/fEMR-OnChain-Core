"""
Registers main fEMR-OnChain data model types to the backend administrative system.
"""
from django.contrib import admin

from .models import MessageOfTheDay, Patient, Contact, PatientDiagnosis, fEMRUser, PatientEncounter,\
     AuditEntry, UnitsSetting, DatabaseChangeLog, Campaign, Instance, Vitals,\
         Treatment, Medication, ChiefComplaint, Diagnosis, Photo


from .forms import PatientEncounterForm, TreatmentForm


class TreatmentAdmin(admin.ModelAdmin):
    form = TreatmentForm


class PatientEncounterAdmin(admin.ModelAdmin):
    form = PatientEncounterForm


admin.site.register(Patient)
admin.site.register(fEMRUser)
admin.site.register(PatientEncounter, PatientEncounterAdmin)
admin.site.register(AuditEntry)
admin.site.register(UnitsSetting)
admin.site.register(DatabaseChangeLog)
admin.site.register(Campaign)
admin.site.register(Instance)
admin.site.register(Contact)
admin.site.register(Vitals)
admin.site.register(Treatment, TreatmentAdmin)
admin.site.register(Medication)
admin.site.register(ChiefComplaint)
admin.site.register(Diagnosis)
admin.site.register(PatientDiagnosis)
admin.site.register(Photo)
admin.site.register(MessageOfTheDay)