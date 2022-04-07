from main.templatetags.patient_tags import last_timestamp, mask_social
from model_bakery import baker


def test_mask_social():
    social = "1234"
    assert mask_social(social) == "***-**-1234"


def test_last_timestamp():
    patient = baker.make("main.Patient")
    last_timestamp(patient)
    patient.delete()
