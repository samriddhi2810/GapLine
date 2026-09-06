from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import dashboard_context


@login_required
def home(request):
    context = dashboard_context(request.user)
    return render(request, "dashboard.html", context)

# Create your views here.
