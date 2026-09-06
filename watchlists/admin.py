from django.contrib import admin

from .models import Watchlist, WatchlistItem

admin.site.register(Watchlist)
admin.site.register(WatchlistItem)

# Register your models here.
