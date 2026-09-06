from django.urls import path

from . import views

app_name = "watchlists"

urlpatterns = [
    path("", views.watchlist_page, name="page"),
    path("api/items/", views.add_stock_api, name="add_stock_api"),
    path("api/items/<int:item_id>/mark-understood/", views.mark_understood_api, name="mark_understood_api"),
    path("items/<int:item_id>/remove/", views.remove_stock_view, name="remove_stock"),
]
