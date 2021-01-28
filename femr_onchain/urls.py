"""femr_onchain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:

https://docs.djangoproject.com/en/3.0/topics/http/urls/

Examples:

Function views

1. Add an import:  from my_app import views

2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views

1. Add an import:  from other_app.views import Home

2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf

1. Import the include() function: from django.urls import include, path

2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main.auth_views import change_password, required_change_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    url(r'session_security/', include('session_security.urls')),

    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'),
        name='password_reset'),
    url(r'^password_reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='auth/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='auth/password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='auth/password_reset_complete.html'),
        name='password_reset_complete'),
    path('change_password/', change_password, name='change_password'),
    path('required_change_password/', required_change_password, name='required_change_password'),
]
