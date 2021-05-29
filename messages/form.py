from django.forms.models import ModelForm
from .models import Message

class MessageForm(ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Message
        fields = '__all__'