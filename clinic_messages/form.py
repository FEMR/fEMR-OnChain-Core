from django.forms.models import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Message


class MessageForm(ModelForm):
    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn btn-primary'))
    helper.form_method = 'POST'
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
    
    class Meta:
        model = Message
        fields = '__all__'