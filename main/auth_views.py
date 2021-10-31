"""
View functions geared toward user authentication.

All views, except auth views and the index view,
should be considered to check for a valid and authenticated user.

If one is not found, they will direct to the appropriate error page.
"""
from axes.utils import reset
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, DataError
from django.shortcuts import redirect, render
from django.utils import timezone
from silk.profiling.profiler import silk_profile

from main.background_tasks import (
    check_admin_permission,
    reset_sessions,
    check_browser,
    run_user_deactivate,
)
from main.femr_admin_views import get_client_ip
from main.forms import RegisterForm, LoginForm
from main.models import AuditEntry, UserSession, fEMRUser


@silk_profile("registration")
def register(request):
    """
    Allows new user registration.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if request.user.is_authenticated:
        return redirect("/main")
    elif request.method == "POST":
        form = RegisterForm(request.POST)
        error = ""
        if form.is_valid():
            try:
                try:
                    existing_email = User.objects.get(email=form.cleaned_data["email"])
                except User.DoesNotExist:
                    existing_email = False
                if existing_email:
                    raise MultipleObjectsReturned
                u = User()
                u.email = form.cleaned_data["email"]
                u.username = form.cleaned_data["username"]
                u.set_password(form.cleaned_data["password"])
                u.first_name = form.cleaned_data["first"]
                u.last_name = form.cleaned_data["last"]
                login(request, u)
                return_response = redirect("/thanks")
            except IntegrityError:
                error = "An account already exists using that username."
            except MultipleObjectsReturned:
                error = "An account already exists with that email address."
            except DataError as e:
                error = str(e)
        return_response = render(
            request, "auth/register.html", {"form": RegisterForm(), "error": error}
        )
    else:
        return_response = render(
            request, "auth/register.html", {"form": RegisterForm(), "error": ""}
        )
    return return_response


@silk_profile("thank-you-for-registering")
def thank_you_for_registering(request):
    """
    Registration success return_response.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    return render(request, "auth/thank_you_for_registering.html")


@silk_profile("all_locked")
def all_locked(request):
    """
    Response for cases where a page requires an authenticated user with elevated privileges.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    return render(request, "auth/all_locked.html")


@silk_profile("not-logged-in")
def not_logged_in(request):
    """
    Response for cases where a page requires an authenticated user with elevated privileges.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    return render(request, "auth/not_logged_in.html")


@silk_profile("please-register")
def please_register(request):
    """
    Response for cases where a page requires any general authenticated user.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    return render(request, "auth/please_register.html")


@silk_profile("permission-denied")
def permission_denied(request):
    """
    Response on pages that require higher privileges than the requesting user holds.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    return render(request, "auth/permission_denied.html")


@silk_profile("login_view")
def login_view(request):
    """
    Handles authenticating existing users.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if not check_browser(request):
        return render(request, "data/stop.html")
    reset_sessions()
    run_user_deactivate()
    if request.user.is_authenticated:
        return redirect("main:home")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request=request,
                username=request.POST["username"],
                password=request.POST["password"],
            )
            if user is not None:
                login(request, user)
                if UserSession.objects.filter(user=request.user).exists():
                    form = LoginForm()
                    logout(request)
                    return render(
                        request,
                        "auth/login.html",
                        {
                            "error_message": "This user is logged in elsewhere, "
                            "or the last session wasn't "
                            "ended correctly. Either log out of your last session, "
                            "or wait for that session to end in one minute.",
                            "form": form,
                        },
                    )
                is_admin = request.user.groups.filter(name="fEMR Admin").exists()
                if (
                    len(user.campaigns.all()) == 1
                    and not user.campaigns.all()[0].active
                ):
                    if not is_admin:
                        return redirect("main:all_locked")
                    else:
                        request.session["campaign"] = "RECOVERY MODE"
                        if "remember_me" in request.POST:
                            return_response = redirect("main:home")
                            return_response.set_cookie(
                                "username", request.POST["username"]
                            )
                            return return_response
                        else:
                            return redirect("main:home")
                if (timezone.now() - user.password_reset_last).days >= 90:
                    return redirect("required_change_password")
                elif not user.change_password:
                    if "remember_me" in request.POST:
                        return_response = redirect("main:home")
                        return_response.set_cookie("username", request.POST["username"])
                        return return_response
                    else:
                        return redirect("main:home")
                else:
                    return redirect("required_change_password")
            else:
                ip = get_client_ip(request)
                AuditEntry.objects.create(
                    action="user_login_failed", ip=ip, username=request.POST["username"]
                )
                if "username" in request.COOKIES:
                    form = LoginForm(initial={"username": request.COOKIES["username"]})
                else:
                    form = LoginForm()
                try:
                    u = fEMRUser.objects.get(username=request.POST["username"])
                    if u.is_active:
                        error_message = "Invalid username or password."
                    else:
                        error_message = "Your account has been locked. "
                        "Please contact your administrator."
                except fEMRUser.DoesNotExist:
                    error_message = "Invalid username or password."
                return render(
                    request,
                    "auth/login.html",
                    {"error_message": error_message, "form": form},
                )
    else:
        if "username" in request.COOKIES:
            form = LoginForm(initial={"username": request.COOKIES["username"]})
        else:
            form = LoginForm()
        return render(request, "auth/login.html", {"form": form})


@silk_profile("logout-view")
def logout_view(request):
    """
    Handles logout.

    :param request: Django Request object.
    :return: HTTPResponse.
    """
    if not isinstance(request.user, AnonymousUser):
        UserSession.objects.filter(user=request.user).delete()
    logout(request)
    if "campaign" in request.session:
        del request.session["campaign"]
    return_response = redirect("main:login_view")
    if "username" in request.COOKIES:
        return_response.delete_cookie("username")
    return return_response


@silk_profile("change-password")
def change_password(request):
    """
    Handle requests to change passwords for the AUTH_USER model.

    :param request: Django request object. Provided by the URLS config.
    :return: Renders the change_password page as an HTTPResponse.
    """
    error = ""
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                user.change_password = False
                user.password_reset_last = timezone.now()
                user.save()
                return redirect("main:index")
            else:
                error = "Something went wrong."
        else:
            form = PasswordChangeForm(request.user)
        return render(
            request,
            "auth/change_password.html",
            {"user": request.user, "form": form, "error_message": error},
        )
    else:
        return redirect("main:not_logged_in")


@silk_profile("required-change-password")
def required_change_password(request):
    """
    Handle requests to change passwords for the AUTH_USER model.

    :param request: Django request object. Provided by the URLS config.
    :return: Renders the change_password page as an HTTPResponse.
    """
    error = ""
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                user.change_password = False
                user.save()
                return redirect("main:index")
            else:
                error = "Something went wrong."
        else:
            form = PasswordChangeForm(request.user)
        return render(
            request,
            "auth/required_change_password.html",
            {"user": request.user, "form": form, "error_message": error},
        )
    else:
        return redirect("main:not_logged_in")


def reset_lockouts(request, username=None):
    if request.user.is_authenticated:
        if check_admin_permission(request.user):
            if username is not None:
                reset(username=username)
                return_response = render(
                    request, "admin/user_reset_success.html", {"username": username}
                )
            else:
                return_response = render(request, "admin/user_reset_no_success.html")
        else:
            return_response = redirect("main:permission_denied")
    else:
        return_response = redirect("main:not_logged_in")
    return return_response
