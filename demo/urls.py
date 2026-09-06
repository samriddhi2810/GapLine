from django.urls import path

from . import views

app_name = "demo"

urlpatterns = [
    path("controls/", views.controls, name="controls"),
    path("advance/", views.advance_view, name="advance"),
    path("reset/", views.reset_view, name="reset"),
    path("api/advance/", views.advance_api, name="advance_api"),
    path("api/reset/", views.reset_api, name="reset_api"),
]
