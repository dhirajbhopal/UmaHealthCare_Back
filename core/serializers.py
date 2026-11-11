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


from rest_framework import serializers
from django.db import transaction

from .models import PartyDetail, TaxInvoice, TaxInvoiceItem


# =========================================
# PARTY DETAIL SERIALIZER
# =========================================

class PartyDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartyDetail
        fields = "__all__"


# =========================================
# INVOICE ITEM SERIALIZER
# =========================================

class InvoiceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxInvoiceItem
        fields = [
            "id",
            "item_no",
            "item_name",
            "hsn_code",
            "quantity",
            "unit",
            "rate",
            "cgst_rate",
            "sgst_rate",
            "discount",
            "total_amount",
        ]

        read_only_fields = ["id", "item_no", "total_amount"]


# =========================================
# TAX INVOICE DISPLAY SERIALIZER
# =========================================

class TaxInvoiceSerializer(serializers.ModelSerializer):

    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = TaxInvoice
        fields = "__all__"


from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from rest_framework import serializers

from .models import TaxInvoice, TaxInvoiceItem


# =========================================
# TAX INVOICE CREATE SERIALIZER
# DISCOUNT AFTER GST
# =========================================

class TaxInvoiceCreateSerializer(serializers.ModelSerializer):

    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = TaxInvoice
        fields = [
            "name",
            "email",
            "mobile_no",
            "address",
            "shipping_add",
            "gstin_uin",
            "invoice_date",
            "items",
        ]

    @transaction.atomic
    def create(self, validated_data):

        items_data = validated_data.pop("items")

        # CREATE INVOICE MASTER
        invoice = TaxInvoice.objects.create(**validated_data)

        # CREATE INVOICE ITEMS
        for index, item_data in enumerate(items_data, start=1):

            quantity = Decimal(str(item_data.get("quantity") or 0))
            rate = Decimal(str(item_data.get("rate") or 0))
            discount = Decimal(str(item_data.get("discount") or 0))

<<<<<<< HEAD
            cgst_rate = Decimal(str(item_data.get("cgst_rate") or 0))
            sgst_rate = Decimal(str(item_data.get("sgst_rate") or 0))
=======
            taxable_amount = max(
                Decimal("0"),
                (qty * rate)
            )
>>>>>>> 8eeab4dc806c990afe5f4ce9d3c86eadc722b7e7

            # =================================
            # SUBTOTAL
            # =================================

            subtotal = quantity * rate

<<<<<<< HEAD
            # =================================
            # GST ON FULL SUBTOTAL
            # =================================

            cgst = subtotal * cgst_rate / Decimal("100")
            sgst = subtotal * sgst_rate / Decimal("100")

            # =================================
            # DISCOUNT AFTER GST
            # =================================

            total_before_discount = subtotal + cgst + sgst

            if discount < 0 or discount > total_before_discount:
                raise serializers.ValidationError(
                    f"Invalid discount in item row {index}."
                )

            total_amount = (
                total_before_discount - discount
=======
            total = (
                taxable_amount + cgst + sgst-discount
>>>>>>> 8eeab4dc806c990afe5f4ce9d3c86eadc722b7e7
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            # REMOVE CLIENT-SENT TOTAL
            item_data.pop("total_amount", None)

            # SAVE ITEM
            TaxInvoiceItem.objects.create(
                invoice=invoice,
                item_no=index,
                total_amount=total_amount,
                **item_data
            )

        return invoice