from django.shortcuts import redirect


def is_authenticated(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return_response = view_func(request, *args, **kwargs)
        else:
            return_response = redirect("app_mr:not_logged_in")
        return return_response

    return wrap
