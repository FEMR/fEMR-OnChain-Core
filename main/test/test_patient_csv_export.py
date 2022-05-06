from clinic_messages.models import Message
from model_bakery import baker

from main.csvio.patient_csv_export import (
    csv_export_handler,
    dict_builder,
    patient_processing_loop,
)
from main.models import Patient, fEMRUser


def test_patient_processing_loop():
    campaign = baker.make("main.Campaign")
    patient = baker.make("main.Patient", campaign=[campaign])
    baker.make("main.PatientEncounter", patient=patient, campaign=campaign)
    patient_data = Patient.objects.filter(campaign=campaign)
    patient_rows = []
    vitals_dict = {}
    treatments_dict = {}
    hpis_dict = {}
    max_treatments, max_hpis, max_vitals = dict_builder(
        patient_data, vitals_dict, treatments_dict, hpis_dict
    )
    result = patient_processing_loop(
        patient_data,
        patient_rows,
        campaign,
        vitals_dict,
        max_vitals,
        treatments_dict,
        max_treatments,
        hpis_dict,
        max_hpis,
    )
    print(result)
    assert result == 1


def test_csv_export_handler():
    admin_user = fEMRUser.objects.create_user(
        username="admin",
        password="testingpassword",
        email="admin@email.com",
    )
    user = fEMRUser.objects.create_user(
        username="testcsvexporthandler",
        password="testingpassword",
        email="testcsvexporthandler@email.com",
    )
    user.change_password = False
    campaign = baker.make("main.Campaign")
    campaign.active = True
    campaign.save()
    user.campaigns.add(campaign)
    user.save()
    patient = baker.make("main.Patient", campaign=[campaign])
    baker.make("main.PatientEncounter", patient=patient, campaign=campaign)
    csv_export_handler(user.id, campaign.id)
    assert Message.objects.filter(recipient=user).count() == 1
    user.delete()
    admin_user.delete()
