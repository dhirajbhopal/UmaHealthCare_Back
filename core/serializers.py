from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserLoginInfo , User, updates

from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from .models import TaxInvoice, TaxInvoiceItem, PartyDetail
from rest_framework import serializers

# Automatically fetches your project's active User model (Custom or Default)
User = get_user_model()

class UserLoginInfoSerializer(serializers.ModelSerializer):
    # Allows React to send an integer (ID) for the user field
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = UserLoginInfo
        fields = [
            'id', 
            'user', 
            'ip_address', 
            'city', 
            'region', 
            'country', 
            'browser', 
            'os', 
            'device', 
            'created_at'  # Included assuming you have a timestamp field
        ]
        # 'id' and 'created_at' should be read-only so React doesn't have to provide them
        read_only_fields = ['id', 'created_at']

    def validate_ip_address(self, value):
        """
        Optional: Basic sanitation field validation. 
        Ensures that if React sends an empty IP string, it defaults nicely.
        """
        if not value or value.strip() == "":
            return "0.0.0.0"
        return value


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


    #Vijay Detail////////////////////////////////////////////////////


class PartyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyDetail
        fields = [
            "id",
            "name",
            "email",
            "mobilno",
            "address",
            "shipping_add",
            "gstin_uin",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Party name is required.")
        return value


# =========================================
# INPUT SERIALIZER FOR EACH ITEM
# =========================================

class TaxInvoiceItemInputSerializer(serializers.Serializer):

    item_name = serializers.CharField(max_length=200)
    hsn_code = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )

    quantity = serializers.DecimalField(
        max_digits=10, decimal_places=2
    )

    unit = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )

    rate = serializers.DecimalField(
        max_digits=12, decimal_places=2
    )

    cgst_rate = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    sgst_rate = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )


# =========================================
# INVOICE CREATE SERIALIZER
# =========================================

class TaxInvoiceCreateSerializer(serializers.ModelSerializer):

    items = TaxInvoiceItemInputSerializer(many=True)

    class Meta:
        model = TaxInvoice
        fields = [
            "invoice_date",
            "customer_name",
            "email",
            "mobile_no",
            "address",
            "shipping_add",
            "gstin_uin",
            "items"
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one invoice item is required."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):

        items_data = validated_data.pop("items")

        # Create invoice master
        invoice = TaxInvoice.objects.create(**validated_data)

        # Create all line items
        for item_no, item in enumerate(items_data, start=1):

            qty = item["quantity"]
            rate = item["rate"]
            discount = item["discount"]

            taxable_amount = max(
                Decimal("0"),
                (qty * rate) - discount
            )

            cgst = (
                taxable_amount * item["cgst_rate"]
                / Decimal("100")
            )

            sgst = (
                taxable_amount * item["sgst_rate"]
                / Decimal("100")
            )

            total = (
                taxable_amount + cgst + sgst
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            TaxInvoiceItem.objects.create(
                invoice=invoice,
                item_no=item_no,
                total_amount=total,
                **item
            )

        return invoice


# =========================================
# INVOICE OUTPUT SERIALIZERS
# =========================================

class TaxInvoiceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxInvoiceItem
        fields = "__all__"


class TaxInvoiceSerializer(serializers.ModelSerializer):

    items = TaxInvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = TaxInvoice
        fields = "__all__"
