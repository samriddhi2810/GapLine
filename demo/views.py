from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from market.services import get_replay_state
from .services import advance_demo, reset_demo


@login_required
def controls(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Demo controls require staff access.")
    return render(request, "demo_controls.html", {"replay_state": get_replay_state()})


@require_POST
@login_required
def advance_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Demo controls require staff access.")
    advance_demo(1)
    return redirect("dashboard:home")


@require_POST
@login_required
def reset_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Demo controls require staff access.")
    reset_demo()
    return redirect("dashboard:home")


@api_view(["POST"])
@permission_classes([IsAdminUser])
def advance_api(request):
    state = advance_demo(1)
    return Response({"current_index": state.current_index, "current_as_of": state.current_as_of})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def reset_api(request):
    reset_demo()
    state = get_replay_state()
    return Response({"current_index": state.current_index, "current_as_of": state.current_as_of})

# Create your views here.
