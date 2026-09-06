from django.urls import path

from . import views

app_name = "receipts"

urlpatterns = [
    path("<int:receipt_id>/", views.receipt_page, name="detail"),
    path("api/<int:receipt_id>/", views.receipt_api, name="api_detail"),
]
