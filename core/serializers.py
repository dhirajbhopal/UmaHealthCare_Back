from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserLoginInfo , User

from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
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




from rest_framework import serializers
from django.utils import timezone
from secrets import token_hex

from .models import (
    User,
    UserLoginInfo,
    Department,
    Staff,
    Doctor,
    Patient,
    OPDTokenCounter,
    OPDAppointment,
    PatientVisit,
    PatientTreatment,
    PatientVital,
    MedicalReport,
    HospitalInvoice,
    HospitalInvoiceItem,
    Medicine,
    MedicineBatch,
    MedicineSupplier,
    MedicinePurchaseReceipt,
    MedicinePurchaseItem,
    MedicineStockMovement,
    PatientAdmission,
    PatientPayment,
    HospitalExpense,
    HospitalAuditLog,
)


# =====================================================
# 1. USER MANAGEMENT
# =====================================================

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False
    )

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ["id", "last_login", "date_joined"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        if not password:
            raise serializers.ValidationError({
                "password": "Password is required."
            })

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserLoginInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLoginInfo
        fields = "__all__"
        read_only_fields = "__all__"


# =====================================================
# 2. DEPARTMENT MANAGEMENT
# =====================================================

class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 3. STAFF MANAGEMENT
# =====================================================

class StaffSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.department_name",
        read_only=True
    )

    class Meta:
        model = Staff
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 4. DOCTOR MANAGEMENT
# =====================================================

class DoctorSerializer(serializers.ModelSerializer):

    staff_name = serializers.CharField(
        source="staff.full_name",
        read_only=True
    )

    staff_code = serializers.CharField(
        source="staff.staff_code",
        read_only=True
    )

    department_name = serializers.CharField(
        source="staff.department.department_name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Doctor
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 5. PATIENT MANAGEMENT
# =====================================================

class PatientSerializer(serializers.ModelSerializer):

    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = "__all__"

        read_only_fields = [
            "id",
            "patient_code",
            "registration_date",
            "created_at",
        ]

    def get_age(self, obj):
        if not obj.date_of_birth:
            return None

        today = timezone.localdate()
        dob = obj.date_of_birth

        return (
            today.year - dob.year
            - ((today.month, today.day) < (dob.month, dob.day))
        )

    def create(self, validated_data):

        validated_data["patient_code"] = (
            f"PAT-{timezone.localdate():%Y%m%d}-"
            f"{token_hex(3).upper()}"
        )

        return super().create(validated_data)

    def validate_mobile(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Mobile number is required."
            )

        return value


# =====================================================
# 6. OPD TOKEN COUNTER
# =====================================================

class OPDTokenCounterSerializer(serializers.ModelSerializer):

    doctor_name = serializers.CharField(
        source="doctor.staff.full_name",
        read_only=True
    )

    class Meta:
        model = OPDTokenCounter
        fields = "__all__"
        read_only_fields = ["id", "last_token_number"]


# =====================================================
# 7. OPD APPOINTMENT
# =====================================================

class OPDAppointmentSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    patient_code = serializers.CharField(
        source="patient.patient_code",
        read_only=True
    )

    patient_mobile = serializers.CharField(
        source="patient.mobile",
        read_only=True
    )

    doctor_name = serializers.CharField(
        source="doctor.staff.full_name",
        read_only=True
    )

    class Meta:
        model = OPDAppointment
        fields = "__all__"
        read_only_fields = [
            "id",
            "booking_reference",
            "token_number",
            "booking_datetime",
        ]


# =====================================================
# 8. PATIENT VISIT
# =====================================================

class PatientVisitSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    patient_code = serializers.CharField(
        source="patient.patient_code",
        read_only=True
    )

    doctor_name = serializers.CharField(
        source="doctor.staff.full_name",
        read_only=True
    )

    class Meta:
        model = PatientVisit
        fields = "__all__"
        read_only_fields = [
            "id",
            "visit_number",
            "created_at",
        ]


# =====================================================
# 9. PATIENT TREATMENT
# =====================================================

class PatientTreatmentSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    doctor_name = serializers.CharField(
        source="doctor.staff.full_name",
        read_only=True
    )

    visit_number = serializers.CharField(
        source="visit.visit_number",
        read_only=True
    )

    class Meta:
        model = PatientTreatment
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 10. PATIENT VITALS
# =====================================================

class PatientVitalSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    class Meta:
        model = PatientVital
        fields = "__all__"
        read_only_fields = [
            "id",
            "recorded_at",
        ]


# =====================================================
# 11. MEDICAL REPORTS
# =====================================================

class MedicalReportSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    patient_code = serializers.CharField(
        source="patient.patient_code",
        read_only=True
    )

    doctor_name = serializers.CharField(
        source="requested_by.staff.full_name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = MedicalReport
        fields = "__all__"
        read_only_fields = [
            "id",
            "report_number",
            "created_at",
        ]


# =====================================================
# 12. HOSPITAL INVOICE
# =====================================================

class HospitalInvoiceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = HospitalInvoiceItem
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class HospitalInvoiceSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    patient_code = serializers.CharField(
        source="patient.patient_code",
        read_only=True
    )

    items = HospitalInvoiceItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = HospitalInvoice
        fields = "__all__"
        read_only_fields = [
            "id",
            "invoice_number",
            "created_at",
        ]


# =====================================================
# 13. MEDICINE MANAGEMENT
# =====================================================

class MedicineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicine
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 14. MEDICINE BATCH
# =====================================================

class MedicineBatchSerializer(serializers.ModelSerializer):

    medicine_name = serializers.CharField(
        source="medicine.medicine_name",
        read_only=True
    )

    medicine_code = serializers.CharField(
        source="medicine.medicine_code",
        read_only=True
    )

    class Meta:
        model = MedicineBatch
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 15. MEDICINE SUPPLIER
# =====================================================

class MedicineSupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineSupplier
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 16. MEDICINE PURCHASE RECEIPT
# =====================================================

class MedicinePurchaseItemSerializer(serializers.ModelSerializer):

    medicine_name = serializers.CharField(
        source="medicine.medicine_name",
        read_only=True
    )

    class Meta:
        model = MedicinePurchaseItem
        fields = "__all__"
        read_only_fields = ["id"]


class MedicinePurchaseReceiptSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.supplier_name",
        read_only=True
    )

    items = MedicinePurchaseItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = MedicinePurchaseReceipt
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 17. MEDICINE STOCK MOVEMENT
# =====================================================

class MedicineStockMovementSerializer(serializers.ModelSerializer):

    medicine_name = serializers.CharField(
        source="medicine.medicine_name",
        read_only=True
    )

    batch_number = serializers.CharField(
        source="batch.batch_number",
        read_only=True
    )

    class Meta:
        model = MedicineStockMovement
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 18. PATIENT ADMISSION
# =====================================================

class PatientAdmissionSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    patient_code = serializers.CharField(
        source="patient.patient_code",
        read_only=True
    )

    doctor_name = serializers.CharField(
        source="doctor.staff.full_name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = PatientAdmission
        fields = "__all__"
        read_only_fields = ["id", "admission_number"]


# =====================================================
# 19. PATIENT PAYMENT
# =====================================================

class PatientPaymentSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )

    invoice_number = serializers.CharField(
        source="invoice.invoice_number",
        read_only=True
    )

    class Meta:
        model = PatientPayment
        fields = "__all__"
        read_only_fields = [
            "id",
            "receipt_number",
        ]


# =====================================================
# 20. HOSPITAL EXPENSE
# =====================================================

class HospitalExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = HospitalExpense
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =====================================================
# 21. HOSPITAL AUDIT LOG
# =====================================================

class HospitalAuditLogSerializer(serializers.ModelSerializer):

    staff_name = serializers.CharField(
        source="staff.full_name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = HospitalAuditLog
        fields = "__all__"
        read_only_fields = "__all__"
