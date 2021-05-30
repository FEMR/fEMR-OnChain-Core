from django.conf.urls import url
from clinic_messages.views import index, new_message, reply_message
from django.urls import path


app_name = 'clinic_messages'

urlpatterns = [
    url(r'^$', index, name='index'),
    path(r'new_message/',
         new_message, name='new_message'),
    path(r'reply_message/<int:message_id>/<int:sender_id>',
         reply_message, name='reply_message'),
]
