from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ChangeReceipt
from .serializers import ChangeReceiptSerializer


@login_required
def receipt_page(request, receipt_id: int):
    receipt = get_object_or_404(
        ChangeReceipt.objects.select_related("watchlist_item", "checkpoint"),
        id=receipt_id,
        user=request.user,
    )
    return render(request, "receipt.html", {"receipt": receipt})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def receipt_api(request, receipt_id: int):
    receipt = get_object_or_404(ChangeReceipt, id=receipt_id, user=request.user)
    return Response(ChangeReceiptSerializer(receipt).data)

# Create your views here.
