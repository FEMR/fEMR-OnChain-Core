import math
from silk.profiling.profiler import silk_profile


@silk_profile("history_view_imperial")
def history_view_imperial(form, encounter):
    form.initial = {
        "body_mass_index": encounter.body_mass_index,
        "smoking": encounter.smoking,
        "history_of_diabetes": encounter.history_of_diabetes,
        "history_of_hypertension": encounter.history_of_hypertension,
        "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
        "alcohol": encounter.alcohol,
        "chief_complaint": [c.pk for c in encounter.chief_complaint.all().iterator()],
        "patient_history": encounter.patient_history,
        "community_health_worker_notes": encounter.community_health_worker_notes,
        "body_height_primary": math.floor(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            // 12
        ),
        "body_height_secondary": round(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            % 12,
            2,
        ),
        "body_weight": round(
            encounter.body_weight if encounter.body_weight is not None else 0 * 2.2046,
            2,
        ),
    }


@silk_profile("new-vitals-imperial")
def new_vitals_imperial(form, encounter):
    form.initial = {
        "body_mass_index": encounter.body_mass_index,
        "smoking": encounter.smoking,
        "history_of_diabetes": encounter.history_of_diabetes,
        "history_of_hypertension": encounter.history_of_hypertension,
        "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
        "alcohol": encounter.alcohol,
        "chief_complaint": [
            complaint.pk for complaint in encounter.chief_complaint.all().iterator()
        ],
        "patient_history": encounter.patient_history,
        "community_health_worker_notes": encounter.community_health_worker_notes,
        "body_height_primary": math.floor(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            // 12
        ),
        "body_height_secondary": round(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            % 12,
            2,
        ),
        "body_weight": round(encounter.body_weight * 2.2046, 2),
    }


@silk_profile("new_diagnosis_imperial")
def new_diagnosis_imperial(form, encounter):
    form.initial = {
        "body_mass_index": encounter.body_mass_index,
        "smoking": encounter.smoking,
        "history_of_diabetes": encounter.history_of_diabetes,
        "history_of_hypertension": encounter.history_of_hypertension,
        "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
        "alcohol": encounter.alcohol,
        "chief_complaint": [c.pk for c in encounter.chief_complaint.all().iterator()],
        "patient_history": encounter.patient_history,
        "community_health_worker_notes": encounter.community_health_worker_notes,
        "body_height_primary": math.floor(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            // 12
        ),
        "body_height_secondary": round(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            % 12,
            2,
        ),
        "body_weight": round(
            encounter.body_weight if encounter.body_weight is not None else 0 * 2.2046,
            2,
        ),
    }


@silk_profile("update-form-initial-imperial")
def encounter_update_form_initial_imperial(form, encounter):
    form.initial = {
        "body_mass_index": encounter.body_mass_index,
        "smoking": encounter.smoking,
        "history_of_diabetes": encounter.history_of_diabetes,
        "history_of_hypertension": encounter.history_of_hypertension,
        "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
        "alcohol": encounter.alcohol,
        "chief_complaint": [c.pk for c in encounter.chief_complaint.all().iterator()],
        "patient_history": encounter.patient_history,
        "community_health_worker_notes": encounter.community_health_worker_notes,
        "body_height_primary": math.floor(
            (
                (
                    (
                        encounter.body_height_primary
                        if encounter.body_height_primary is not None
                        else 0
                    )
                    * 100
                    + (
                        encounter.body_height_secondary
                        if encounter.body_height_secondary is not None
                        else 0
                    )
                )
                / 2.54
            )
            // 12
        ),
        "body_height_secondary": round(
            (
                (
                    (
                        encounter.body_height_primary
                        if encounter.body_height_primary is not None
                        else 0
                    )
                    * 100
                    + (
                        encounter.body_height_secondary
                        if encounter.body_height_secondary is not None
                        else 0
                    )
                )
                / 2.54
            )
            % 12,
            2,
        ),
        "body_weight": round(
            (encounter.body_weight if encounter.body_weight is not None else 0)
            * 2.2046,
            2,
        ),
    }


@silk_profile("new_treatment_imperial")
def new_treatment_imperial(form, encounter):
    form.initial = {
        "body_mass_index": encounter.body_mass_index,
        "smoking": encounter.smoking,
        "history_of_diabetes": encounter.history_of_diabetes,
        "history_of_hypertension": encounter.history_of_hypertension,
        "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
        "alcohol": encounter.alcohol,
        "chief_complaint": [c.pk for c in encounter.chief_complaint.all().iterator()],
        "patient_history": encounter.patient_history,
        "community_health_worker_notes": encounter.community_health_worker_notes,
        "body_height_primary": math.floor(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            // 12
        ),
        "body_height_secondary": round(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            % 12,
            2,
        ),
        "body_weight": round(encounter.body_weight * 2.2046, 2)
        if encounter.body_weight is not None
        else 0,
    }


@silk_profile("aux-form-imperial")
def aux_form_imperial(form, encounter):
    form.initial = {
        "body_mass_index": encounter.body_mass_index,
        "smoking": encounter.smoking,
        "history_of_diabetes": encounter.history_of_diabetes,
        "history_of_hypertension": encounter.history_of_hypertension,
        "history_of_high_cholesterol": encounter.history_of_high_cholesterol,
        "alcohol": encounter.alcohol,
        "chief_complaint": [c.pk for c in encounter.chief_complaint.all().iterator()],
        "patient_history": encounter.patient_history,
        "community_health_worker_notes": encounter.community_health_worker_notes,
        "body_height_primary": math.floor(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            // 12
        ),
        "body_height_secondary": round(
            (
                (encounter.body_height_primary * 100 + encounter.body_height_secondary)
                / 2.54
            )
            % 12,
            2,
        ),
        "body_weight": round(encounter.body_weight * 2.2046, 2),
    }
