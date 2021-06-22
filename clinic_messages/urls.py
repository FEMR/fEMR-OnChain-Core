from django.conf.urls import url
from clinic_messages.views import delete_message, delete_sent_message, index, new_message, reply_message, sent_box, view_message
from django.urls import path


app_name = 'clinic_messages'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^sent/$', sent_box, name='sent_box'),
    path(r'new_message/',
         new_message, name='new_message'),
    path(r'new_message/<int:sender_id>',
         new_message, name='new_message'),
    path(r'reply_message/<int:message_id>/<int:sender_id>',
         reply_message, name='reply_message'),
    path(r'view_message/<int:message_id>/<int:sender_id>',
         view_message, name='view_message'),
    path(r'delete_message/<int:id>',
         delete_message, name='delete_message'),
    path(r'delete_sent_message/<int:id>',
         delete_sent_message, name='delete_sent_message'),
]
