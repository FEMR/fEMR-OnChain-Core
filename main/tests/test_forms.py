from model_bakery import baker

from main.forms import ChiefComplaintForm


def test_chief_complaint_form():
    chief_complaint = baker.make('main.ChiefComplaint')
    form = ChiefComplaintForm(instance=chief_complaint)
    assert 'text' in form.fields
    assert 'active' in form.fields
