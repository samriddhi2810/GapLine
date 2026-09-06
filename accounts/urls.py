from django.urls import path

from .views import GaplineLoginView, GaplineLogoutView

app_name = "accounts"

urlpatterns = [
    path("login/", GaplineLoginView.as_view(), name="login"),
    path("logout/", GaplineLogoutView.as_view(), name="logout"),
]
