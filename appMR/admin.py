from django.contrib import admin

from .models import SupportTicket, Comment


admin.site.register(SupportTicket)
admin.site.register(Comment)
