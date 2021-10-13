from .models import models, Patient


class SurveyValueSetOption(models.Model):
    code = models.IntegerField()
    display_name = models.CharField(max_length=64)

    def __str__(self):
        return str(self.display_name)


class SurveyValueSet(models.Model):
    options = models.ManyToManyField(SurveyValueSetOption)


class Survey(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    item = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    data_type = models.CharField(max_length=2)
    display_name = models.CharField(max_length=250)

    value_set = models.ForeignKey(SurveyValueSet, on_delete=models.CASCADE)

    valid_range = models.CharField(max_length=1)
    field_length = models.IntegerField()
    comments = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.patient)
