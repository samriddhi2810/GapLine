from django.contrib import admin

from .models import DataIncident, MarketBar, MarketObservation, ReplayState, SymbolStatistic

admin.site.register(MarketObservation)
admin.site.register(MarketBar)
admin.site.register(SymbolStatistic)
admin.site.register(DataIncident)
admin.site.register(ReplayState)

# Register your models here.
