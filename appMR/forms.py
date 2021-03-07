from django.forms import ModelForm, CharField, Textarea


from .models import SupportTicket, Comment


class SupportTicketForm(ModelForm):
    description = CharField(widget=Textarea(attrs={"rows":5, "cols":20}))

    class Meta:
        model = SupportTicket
        fields = [
            'title',
            'description',
            'status',
        ]

class CommentForm(ModelForm):
    comment = CharField(widget=Textarea(attrs={"rows":5, "cols":20}))

    class Meta:
        model = Comment
        fields = ['comment']
