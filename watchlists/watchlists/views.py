from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from checkpoints.services import CheckpointUnavailable, mark_understood
from .models import WatchlistItem
from .serializers import AddStockSerializer, WatchlistItemSerializer
from .services import add_stock, get_or_create_default_watchlist, remove_stock


@login_required
def watchlist_page(request):
    watchlist = get_or_create_default_watchlist(request.user)
    return render(request, "watchlist.html", {"watchlist": watchlist, "symbols": ["INFY", "TCS", "RELIANCE", "HDFCBANK", "ICICIBANK", "TATAMOTORS"]})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_stock_api(request):
    serializer = AddStockSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    watchlist = get_or_create_default_watchlist(request.user)
    item, created = add_stock(request.user, watchlist, serializer.validated_data["symbol"])
    return Response({"created": created, "item": WatchlistItemSerializer(item).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_understood_api(request, item_id: int):
    item = get_object_or_404(WatchlistItem.objects.select_related("watchlist"), id=item_id, watchlist__user=request.user)
    try:
        checkpoint = mark_understood(request.user, item)
    except CheckpointUnavailable as exc:
        return Response({"detail": str(exc)}, status=409)
    return Response({"checkpoint_id": checkpoint.id, "symbol": checkpoint.symbol, "replay_index": checkpoint.replay_index})


@require_POST
@login_required
def remove_stock_view(request, item_id: int):
    item = get_object_or_404(WatchlistItem.objects.select_related("watchlist"), id=item_id, watchlist__user=request.user)
    remove_stock(request.user, item)
    return redirect("watchlists:page")

# Create your views here.
