from django.urls import path
from django.shortcuts import redirect
from . import views


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


urlpatterns = [
    path("", home, name="home"),

    # Authentication
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # Book CRUD
    path("books/add/", views.add_book, name="add_book"),
    path("books/edit/<int:book_id>/", views.edit_book, name="edit_book"),
    path("books/delete/<int:book_id>/", views.delete_book, name="delete_book"),

    # AI Summary
    path(
        "books/<int:book_id>/summary/",
        views.generate_summary,
        name="generate_summary"
    ),
]