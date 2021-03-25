"""
Registers main fEMR-OnChain data model types to the backend administrative system.
"""
from django.contrib import admin

from .models import Patient, Contact, fEMRUser, PatientEncounter, AuditEntry, UnitsSetting, DatabaseChangeLog, Campaign, Instance

admin.site.register(Patient)
admin.site.register(fEMRUser)
admin.site.register(PatientEncounter)
admin.site.register(AuditEntry)
admin.site.register(UnitsSetting)
admin.site.register(DatabaseChangeLog)
admin.site.register(Campaign)
admin.site.register(Instance)
admin.site.register(Contact)
