"""
app_mr URL configurations.
"""
from django.urls import path, re_path

from .views import (
    not_logged_in,
    bug_list_view,
    bug_detail_view,
    post_comment_view,
    new_bug_view,
    change_bug_list_view,
)

# pylint: disable=C0103
app_name = "app_mr"

urlpatterns = [
    re_path(r"^$", bug_list_view, name="index"),
    path(r"list/<int:ticket_type>", bug_list_view, name="bug_list_view"),
    re_path(r"^new/$", new_bug_view, name="new_bug_view"),
    path(r"detail/<int:ticket_id>", bug_detail_view, name="bug_detail_view"),
    path(r"comment/<int:bug_id>", post_comment_view, name="post_comment_view"),
    path(
        r"change/<int:ticket_type>", change_bug_list_view, name="change_bug_list_view"
    ),
    re_path(r"^not_logged_in/$", not_logged_in, name="not_logged_in"),
]
