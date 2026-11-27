from django.db import models
import os
import datetime
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models, transaction 
from django.db.models import Max
from pathlib import Path
from django.db.models import Q




# Create your models here.

def filepathadmin(req,filename):
    old_filename = filename
    timeNow = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename= "%s%s" % (timeNow,old_filename)
    return os.path.join('uploads/',filename)
  


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff being True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(email=email, password=password, **extra_fields)



class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, blank=False ,null=False)
    email = models.EmailField(unique=True,null=False)
    #image=models.ImageField(upload_to=filepathadmin,null=True,blank=True,default='staticfiles/images/PATEL_LOGO.png')
    mobileno=models.CharField(max_length=15,null=True,blank=True)
    gender=models.CharField(max_length=15,null=True,blank=True)
    role=models.CharField(max_length=30,null=True,blank=True)
    address=models.CharField(max_length=200,null=True,blank=True)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    image = models.ImageField(
        upload_to='uploads/',
        blank=True,
        null=True,
        default='staticfiles/images/PATEL_LOGO.png'
    )


    def __str__(self):
        return self.username



class UserLoginInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"





class Department(models.Model):
    department_code = models.CharField(max_length=20, unique=True)
    department_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departments"
        ordering = ["department_name"]

    def __str__(self):
        return self.department_name


class Staff(models.Model):
    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        OTHER = "Other", "Other"

    class EmploymentType(models.TextChoices):
        PERMANENT = "Permanent", "Permanent"
        CONTRACT = "Contract", "Contract"
        PART_TIME = "Part Time", "Part Time"
        VISITING = "Visiting", "Visiting"

    class Status(models.TextChoices):
        ACTIVE = "Active", "Active"
        INACTIVE = "Inactive", "Inactive"
        RESIGNED = "Resigned", "Resigned"
        TERMINATED = "Terminated", "Terminated"

    staff_code = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    designation = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="staff_members"
    )
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices,
        default=EmploymentType.PERMANENT
    )
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    staff_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "staff"
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["staff_code"]),
            models.Index(fields=["mobile"]),
            models.Index(fields=["staff_status"]),
        ]

    def __str__(self):
        return f"{self.staff_code} - {self.full_name}"


class Doctor(models.Model):
    doctor_code = models.CharField(max_length=30, unique=True)
    staff = models.OneToOneField(
        Staff, on_delete=models.PROTECT, related_name="doctor_profile"
    )
    specialization = models.CharField(max_length=150, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    followup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    opd_start_time = models.TimeField(blank=True, null=True)
    opd_end_time = models.TimeField(blank=True, null=True)
    is_online_booking = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "doctors"
        ordering = ["staff__full_name"]

    def __str__(self):
        return f"{self.doctor_code} - {self.staff.full_name}"


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        OTHER = "Other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "Active", "Active"
        INACTIVE = "Inactive", "Inactive"

    patient_code = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    father_husband_name = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    mobile = models.CharField(max_length=20)
    alternate_mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_mobile = models.CharField(max_length=20, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(default=timezone.now)
    patient_status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patients"
        ordering = ["-registration_date"]
        indexes = [
            models.Index(fields=["mobile"]),
            models.Index(fields=["full_name"]),
            models.Index(fields=["patient_code"]),
        ]

    def __str__(self):
        return f"{self.patient_code} - {self.full_name}"


class OPDTokenCounter(models.Model):
    doctor = models.ForeignKey(
        Doctor, on_delete=models.PROTECT, related_name="token_counters"
    )
    token_date = models.DateField()
    last_token_number = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "opd_token_counters"
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "token_date"],
                name="uq_doctor_token_date",
            )
        ]

    def __str__(self):
        return f"{self.doctor} - {self.token_date}: {self.last_token_number}"


class OPDAppointment(models.Model):
    class AppointmentType(models.TextChoices):
        NEW = "New", "New"
        FOLLOWUP = "Followup", "Followup"
        EMERGENCY = "Emergency", "Emergency"

    class BookingSource(models.TextChoices):
        ONLINE = "Online", "Online"
        COUNTER = "Counter", "Counter"
        PHONE = "Phone", "Phone"
        REFERRAL = "Referral", "Referral"

    class Status(models.TextChoices):
        BOOKED = "Booked", "Booked"
        CONFIRMED = "Confirmed", "Confirmed"
        WAITING = "Waiting", "Waiting"
        IN_CONSULTATION = "In Consultation", "In Consultation"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"
        NO_SHOW = "No Show", "No Show"

    booking_reference = models.CharField(max_length=40, unique=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="opd_appointments"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.PROTECT, related_name="opd_appointments"
    )
    appointment_date = models.DateField()
    token_number = models.PositiveIntegerField()
    appointment_type = models.CharField(
        max_length=20, choices=AppointmentType.choices, default=AppointmentType.NEW
    )
    booking_source = models.CharField(
        max_length=20, choices=BookingSource.choices, default=BookingSource.COUNTER
    )
    appointment_status = models.CharField(
        max_length=25, choices=Status.choices, default=Status.BOOKED
    )
    patient_notes = models.TextField(blank=True, null=True)
    booked_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="opd_bookings_created"
    )
    booking_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "opd_appointments"
        ordering = ["appointment_date", "doctor", "token_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "appointment_date", "token_number"],
                name="uq_doctor_daily_token",
            )
        ]
        indexes = [
            models.Index(fields=["appointment_date"]),
            models.Index(fields=["patient"]),
            models.Index(fields=["appointment_status"]),
        ]

    def __str__(self):
        return f"{self.booking_reference} - Token {self.token_number}"


class PatientVisit(models.Model):
    class VisitType(models.TextChoices):
        OPD = "OPD", "OPD"
        EMERGENCY = "Emergency", "Emergency"
        IPD = "IPD", "IPD"
        FOLLOWUP = "Followup", "Followup"

    class Status(models.TextChoices):
        OPEN = "Open", "Open"
        IN_PROGRESS = "In Progress", "In Progress"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

    visit_number = models.CharField(max_length=40, unique=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="visits"
    )
    appointment = models.ForeignKey(
        OPDAppointment, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="visits"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.PROTECT, related_name="patient_visits"
    )
    visit_type = models.CharField(
        max_length=20, choices=VisitType.choices, default=VisitType.OPD
    )
    visit_date = models.DateTimeField(default=timezone.now)
    chief_complaint = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    clinical_notes = models.TextField(blank=True, null=True)
    treatment_advice = models.TextField(blank=True, null=True)
    next_followup_date = models.DateField(blank=True, null=True)
    visit_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patient_visits"
        ordering = ["-visit_date"]
        indexes = [
            models.Index(fields=["patient", "visit_date"]),
        ]

    def __str__(self):
        return f"{self.visit_number} - {self.patient.full_name}"


class PatientTreatment(models.Model):
    visit = models.ForeignKey(
        PatientVisit, on_delete=models.PROTECT, related_name="treatments"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="treatments"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.PROTECT, related_name="treatments"
    )
    treatment_date = models.DateTimeField(default=timezone.now)
    treatment_name = models.CharField(max_length=255, blank=True, null=True)
    treatment_description = models.TextField(blank=True, null=True)
    procedure_details = models.TextField(blank=True, null=True)
    prescription_notes = models.TextField(blank=True, null=True)
    advice = models.TextField(blank=True, null=True)
    followup_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patient_treatments"
        ordering = ["-treatment_date"]
        indexes = [models.Index(fields=["patient", "treatment_date"])]

    def __str__(self):
        return f"Treatment: {self.patient.full_name} - {self.treatment_date:%d-%m-%Y}"


class PatientVital(models.Model):
    visit = models.ForeignKey(
        PatientVisit, on_delete=models.PROTECT, related_name="vitals"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="vitals"
    )
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)
    pulse_rate = models.PositiveIntegerField(blank=True, null=True)
    spo2 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    respiratory_rate = models.PositiveIntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    recorded_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="vitals_recorded"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patient_vitals"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"Vitals - {self.patient.full_name} - {self.recorded_at:%d-%m-%Y}"


class MedicalReport(models.Model):
    class ReportType(models.TextChoices):
        PATHOLOGY = "Pathology", "Pathology"
        XRAY = "X-Ray", "X-Ray"
        ULTRASOUND = "Ultrasound", "Ultrasound"
        ECG = "ECG", "ECG"
        EEG = "EEG", "EEG"
        ECHO = "2D Echo", "2D Echo"
        CT = "CT Scan", "CT Scan"
        MRI = "MRI", "MRI"
        ENDOSCOPY = "Endoscopy", "Endoscopy"
        OTHER = "Other", "Other"

    class Status(models.TextChoices):
        REQUESTED = "Requested", "Requested"
        SAMPLE_COLLECTED = "Sample Collected", "Sample Collected"
        PROCESSING = "Processing", "Processing"
        COMPLETED = "Completed", "Completed"
        VERIFIED = "Verified", "Verified"
        CANCELLED = "Cancelled", "Cancelled"

    report_number = models.CharField(max_length=40, unique=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="medical_reports"
    )
    visit = models.ForeignKey(
        PatientVisit, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="medical_reports"
    )
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    test_name = models.CharField(max_length=200)
    requested_by = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="reports_requested"
    )
    performed_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="reports_performed"
    )
    sample_collection_date = models.DateTimeField(blank=True, null=True)
    report_date = models.DateTimeField(blank=True, null=True)
    clinical_indication = models.TextField(blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    impression = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    reference_range = models.TextField(blank=True, null=True)
    report_file = models.FileField(
        upload_to="hospital/medical_reports/%Y/%m/", blank=True, null=True
    )
    report_status = models.CharField(
        max_length=25, choices=Status.choices, default=Status.REQUESTED
    )
    verified_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="reports_verified"
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medical_reports"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient"]),
            models.Index(fields=["report_date"]),
            models.Index(fields=["report_status"]),
        ]

    def __str__(self):
        return f"{self.report_number} - {self.test_name}"


class HospitalInvoice(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID = "Unpaid", "Unpaid"
        PARTIAL = "Partial", "Partial"
        PAID = "Paid", "Paid"
        REFUNDED = "Refunded", "Refunded"

    class PaymentMode(models.TextChoices):
        CASH = "Cash", "Cash"
        UPI = "UPI", "UPI"
        CARD = "Card", "Card"
        BANK = "Bank Transfer", "Bank Transfer"
        INSURANCE = "Insurance", "Insurance"
        OTHER = "Other", "Other"

    invoice_number = models.CharField(max_length=40, unique=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="invoices"
    )
    visit = models.ForeignKey(
        PatientVisit, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="invoices"
    )
    invoice_date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID
    )
    payment_mode = models.CharField(
        max_length=20, choices=PaymentMode.choices, blank=True, null=True
    )
    invoice_notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="hospital_invoices_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hospital_invoices"
        ordering = ["-invoice_date"]
        indexes = [
            models.Index(fields=["patient"]),
            models.Index(fields=["invoice_date"]),
            models.Index(fields=["payment_status"]),
        ]

    def __str__(self):
        return self.invoice_number


class HospitalInvoiceItem(models.Model):
    class ServiceType(models.TextChoices):
        OPD = "OPD", "OPD"
        IPD = "IPD", "IPD"
        LAB = "Lab", "Lab"
        RADIOLOGY = "Radiology", "Radiology"
        PROCEDURE = "Procedure", "Procedure"
        SURGERY = "Surgery", "Surgery"
        MEDICINE = "Medicine", "Medicine"
        ROOM = "Room", "Room"
        OTHER = "Other", "Other"

    invoice = models.ForeignKey(
        HospitalInvoice, on_delete=models.CASCADE, related_name="items"
    )
    item_description = models.CharField(max_length=255)
    service_type = models.CharField(
        max_length=20, choices=ServiceType.choices, default=ServiceType.OTHER
    )
    service_id = models.PositiveBigIntegerField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=30, default="Unit")
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hospital_invoice_items"
        indexes = [models.Index(fields=["invoice"])]

    def __str__(self):
        return self.item_description


class Medicine(models.Model):
    medicine_code = models.CharField(max_length=40, unique=True)
    medicine_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    strength = models.CharField(max_length=100, blank=True, null=True)
    dosage_form = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=30, default="PCS")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medicines"
        ordering = ["medicine_name"]
        indexes = [models.Index(fields=["medicine_name"])]

    def __str__(self):
        return f"{self.medicine_code} - {self.medicine_name}"


class MedicineBatch(models.Model):
    medicine = models.ForeignKey(
        Medicine, on_delete=models.PROTECT, related_name="batches"
    )
    batch_number = models.CharField(max_length=100)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_available = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medicine_batches"
        constraints = [
            models.UniqueConstraint(
                fields=["medicine", "batch_number"],
                name="uq_medicine_batch",
            )
        ]
        indexes = [
            models.Index(fields=["expiry_date"]),
            models.Index(fields=["medicine", "expiry_date"]),
        ]

    def __str__(self):
        return f"{self.medicine.medicine_name} - {self.batch_number}"


class MedicineSupplier(models.Model):
    supplier_code = models.CharField(max_length=30, unique=True)
    supplier_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medicine_suppliers"
        ordering = ["supplier_name"]

    def __str__(self):
        return self.supplier_name


class MedicinePurchaseReceipt(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID = "Unpaid", "Unpaid"
        PARTIAL = "Partial", "Partial"
        PAID = "Paid", "Paid"

    class PaymentMode(models.TextChoices):
        CASH = "Cash", "Cash"
        UPI = "UPI", "UPI"
        CARD = "Card", "Card"
        BANK = "Bank Transfer", "Bank Transfer"
        OTHER = "Other", "Other"

    receipt_number = models.CharField(max_length=40, unique=True)
    supplier_invoice_number = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.ForeignKey(
        MedicineSupplier, on_delete=models.PROTECT, related_name="purchase_receipts"
    )
    purchase_date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID
    )
    payment_mode = models.CharField(
        max_length=20, choices=PaymentMode.choices, blank=True, null=True
    )
    purchase_notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="medicine_purchases_received"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medicine_purchase_receipts"
        ordering = ["-purchase_date"]
        indexes = [models.Index(fields=["purchase_date"])]

    def __str__(self):
        return self.receipt_number


class MedicinePurchaseItem(models.Model):
    purchase = models.ForeignKey(
        MedicinePurchaseReceipt, on_delete=models.CASCADE, related_name="items"
    )
    medicine = models.ForeignKey(
        Medicine, on_delete=models.PROTECT, related_name="purchase_items"
    )
    batch = models.ForeignKey(
        MedicineBatch, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="purchase_items"
    )
    batch_number = models.CharField(max_length=100)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    free_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=30, default="PCS")
    purchase_rate = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "medicine_purchase_items"
        indexes = [models.Index(fields=["purchase"])]

    def __str__(self):
        return f"{self.medicine.medicine_name} - {self.batch_number}"


class MedicineStockMovement(models.Model):
    class MovementType(models.TextChoices):
        PURCHASE = "Purchase", "Purchase"
        SALE = "Sale", "Sale"
        RETURN = "Return", "Return"
        ADJUSTMENT = "Adjustment", "Adjustment"
        EXPIRY = "Expiry", "Expiry"
        DAMAGE = "Damage", "Damage"

    medicine = models.ForeignKey(
        Medicine, on_delete=models.PROTECT, related_name="stock_movements"
    )
    batch = models.ForeignKey(
        MedicineBatch, on_delete=models.PROTECT, related_name="stock_movements"
    )
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.PositiveBigIntegerField(blank=True, null=True)
    quantity_in = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_out = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="stock_movements_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medicine_stock_movements"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["medicine", "created_at"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self):
        return f"{self.medicine.medicine_name} - {self.movement_type}"


class PatientAdmission(models.Model):
    class AdmissionType(models.TextChoices):
        GENERAL = "General", "General"
        EMERGENCY = "Emergency", "Emergency"
        SURGERY = "Surgery", "Surgery"
        ICU = "ICU", "ICU"
        NICU = "NICU", "NICU"

    class Status(models.TextChoices):
        ADMITTED = "Admitted", "Admitted"
        DISCHARGED = "Discharged", "Discharged"
        TRANSFERRED = "Transferred", "Transferred"
        CANCELLED = "Cancelled", "Cancelled"

    admission_number = models.CharField(max_length=40, unique=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="admissions"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="admissions"
    )
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(blank=True, null=True)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    bed_number = models.CharField(max_length=50, blank=True, null=True)
    admission_type = models.CharField(
        max_length=20, choices=AdmissionType.choices, default=AdmissionType.GENERAL
    )
    admission_status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ADMITTED
    )
    admission_notes = models.TextField(blank=True, null=True)
    discharge_summary = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "patient_admissions"
        ordering = ["-admission_date"]
        indexes = [
            models.Index(fields=["patient", "admission_date"]),
            models.Index(fields=["admission_status"]),
        ]

    def __str__(self):
        return self.admission_number


class PatientPayment(models.Model):
    class PaymentMode(models.TextChoices):
        CASH = "Cash", "Cash"
        UPI = "UPI", "UPI"
        CARD = "Card", "Card"
        BANK = "Bank Transfer", "Bank Transfer"
        INSURANCE = "Insurance", "Insurance"
        OTHER = "Other", "Other"

    receipt_number = models.CharField(max_length=40, unique=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="payments"
    )
    invoice = models.ForeignKey(
        HospitalInvoice, on_delete=models.PROTECT, related_name="payments"
    )
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PaymentMode.choices)
    transaction_reference = models.CharField(max_length=150, blank=True, null=True)
    received_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="patient_payments_received"
    )
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "patient_payments"
        ordering = ["-payment_date"]
        indexes = [models.Index(fields=["patient", "payment_date"])]

    def __str__(self):
        return self.receipt_number


class HospitalExpense(models.Model):
    expense_number = models.CharField(max_length=40, unique=True)
    expense_date = models.DateField()
    expense_category = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=50, blank=True, null=True)
    paid_to = models.CharField(max_length=200, blank=True, null=True)
    bill_reference = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="expenses_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hospital_expenses"
        ordering = ["-expense_date"]
        indexes = [models.Index(fields=["expense_date", "expense_category"])]

    def __str__(self):
        return self.expense_number


class HospitalAuditLog(models.Model):
    staff = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="audit_logs"
    )
    action_type = models.CharField(max_length=100)
    module_name = models.CharField(max_length=100)
    record_id = models.PositiveBigIntegerField(blank=True, null=True)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hospital_audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module_name", "record_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.module_name} - {self.action_type} - {self.created_at}"

path = Path("/core/models.py")
