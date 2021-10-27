from django.shortcuts import redirect, render


def pharmacy_home_view(request):
    if request.user.is_authenticated:
        return render(request, "")
    else:
        return redirect("main:not_logged_in")
