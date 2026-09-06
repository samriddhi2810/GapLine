from rest_framework import serializers

from .models import ChangeReceipt


class ChangeReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeReceipt
        fields = "__all__"
