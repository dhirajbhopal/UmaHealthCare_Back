from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from core.models import User, UniqueCode, donation, UserLoginInfo, updates
from django.contrib.auth.models import User
from rest_framework import serializers
from django.db.models import Sum
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import get_client_ip, get_geo_info, get_device_info
import json
import os
import base64
import random
import string
import json
import smtplib
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.http import require_GET
import qrcode
from io import BytesIO
from rest_framework.views import APIView
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import (urlsafe_base64_encode,urlsafe_base64_decode)
from django.utils.encoding import force_bytes
from rest_framework import viewsets
#from .serializers import UserSerializer, UniqueCodeSerializer, donationSerializer , UserLoginInfoSerializer ,updatesSerializer
from django.db import IntegrityError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth import get_user_model
from datetime import datetime
from .serializers import UserLoginInfoSerializer
User = get_user_model()

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TaxInvoice , TaxInvoiceItem  , PartyDetail
from .serializers import (TaxInvoiceCreateSerializer,TaxInvoiceSerializer)
from .serializers import PartyDetailSerializer

from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.mail import EmailMessage


# ==========================================
# SIGNUP API
# ==========================================

@method_decorator(csrf_exempt, name='dispatch')
class Signup(View):

    def post(self, request):

        try:
            data = json.loads(request.body)

            email = data.get("email")

            # CHECK EMAIL EXISTS
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Email already registered"
                }, status=400)

            # CREATE USER
            user = User.objects.create(
                username=data.get("username"),
                mobileno=data.get("mobileno"),
                email=email,
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                gender=data.get("gender"),
                address=data.get("address"),
                password=make_password(data.get("password"))
            )

            # =========================
            # ADMIN MAIL
            # =========================

            admin_message = f"""
            <html>
            <body>
            <h1 style='color:red'>
            PATEL JAN KALYAN SEVA SAMITI
            </h1>

            <hr>

            Hello Admin,<br><br>

            One New User has registered.<br><br>

            User Email :-
            <b>{email}</b>

            <br><br>

            Visit :
            <span style='color:red'>
            https://pjkss.pythonanywhere.com/admin/login/?next=/admin/login
            </span>

            <br><br>

            Thanks
            </body>
            </html>
            """

            smtp = smtplib.SMTP(
                host='smtp.gmail.com',
                port=587
            )

            smtp.starttls()

            smtp.login(
                "pjkssinfo@gmail.com",
                "bwqpbkcdutyqheoi"
            )

            msg = MIMEMultipart()

            msg['From'] = "PJKSS ADMIN"
            msg['To'] = "dhirajpatel08@gmail.com"
            msg['Subject'] = "New Registration"

            msg.attach(
                MIMEText(admin_message, 'html')
            )

            smtp.send_message(msg)

            smtp.quit()

            # =========================
            # USER SUCCESS MAIL
            # =========================

            user_message = f"""
            <html>
            <body>

            <h1 style='color:red'>
            PATEL JAN KALYAN SEVA SAMITI
            </h1>

            <hr>

            Hello {email},<br><br>

            Your Registration is Successful.<br><br>

            User ID :-
            <b>{email}</b>

            <br><br>

            Visit :
            <span style='color:red'>
            https://pjkss.com/login
            </span>

            <br><br>

            Thanks

            </body>
            </html>
            """

            smtp = smtplib.SMTP(
                host='smtp.gmail.com',
                port=587
            )

            smtp.starttls()

            smtp.login(
                "pjkssinfo@gmail.com",
                "bwqpbkcdutyqheoi"
            )

            msg = MIMEMultipart()

            msg['From'] = "PJKSS ADMIN"
            msg['To'] = email
            msg['Subject'] = "Registration Successful"

            msg.attach(
                MIMEText(user_message, 'html')
            )

            smtp.send_message(msg)

            smtp.quit()

            return JsonResponse({
                "success": True,
                "message": "Registration successful",
                "user_id": user.id
            }, status=201)

        except IntegrityError:

            return JsonResponse({
                "success": False,
                "message": "Email already exists"
            }, status=400)

        except Exception as e:

            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=500)


# ==========================================
# GENERATE OTP
# ==========================================

def generateOTP(n):

    range_start = 10 ** (n - 1)

    range_end = (10 ** n) - 1

    return random.randint(
        range_start,
        range_end
    )


# ==========================================
# SEND MAIL FUNCTION
# ==========================================

def sendmail(email, otp):

    try:

        message = f"""
        <html>
        <body>

        <h1 style='color:red'>
        PATEL JAN KALYAN SEVA SAMITI
        </h1>

        <hr>

        Hello {email},<br><br>

        Please enter OTP to complete registration.

        <br><br>

        Your OTP is :
        <span style='color:red'>
        {otp}
        </span>

        <br><br>

        Please don't share OTP with anyone.

        <br><br>

        Thanks

        </body>
        </html>
        """

        smtp = smtplib.SMTP(
            host='smtp.gmail.com',
            port=587
        )

        smtp.starttls()

        smtp.login(
            "pjkssinfo@gmail.com",
            "bwqpbkcdutyqheoi"
        )

        msg = MIMEMultipart()

        msg['From'] = "PJKSS ADMIN"
        msg['To'] = email
        msg['Subject'] = "Registration OTP"

        msg.attach(
            MIMEText(message, 'html')
        )

        smtp.send_message(msg)

        smtp.quit()

        return True

    except Exception as e:

        print(e)

        return False


# ==========================================
# SEND OTP API
# ==========================================

@csrf_exempt
def sendotp_api(request):

    if request.method != "POST":

        return JsonResponse({
            "success": False,
            "message": "POST method required"
        })

    try:

        data = json.loads(request.body)

        email = data.get("email")

        if not email:

            return JsonResponse({
                "success": False,
                "message": "Email required"
            })

        otp = generateOTP(6)

        check = sendmail(email, otp)

        if check:

            request.session['loginotp'] = otp

            return JsonResponse({
                "success": True,
                "message": "OTP Sent Successfully",
                "otp": otp
            })

        else:

            return JsonResponse({
                "success": False,
                "message": "OTP Sending Failed"
            })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        })
# =========================================
# LOGIN API
# =========================================
@csrf_exempt
def login_api(request):

    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        try:

            user = User.objects.get(email=email)

            # CHECK PASSWORD
            if user.check_password(password):

                # VERY IMPORTANT
                user.backend = (
                    "django.contrib.auth.backends.ModelBackend"
                )

                # LOGIN SESSION
                login(request, user)

                return JsonResponse({
                    "success": True,
                    "message": "Login Successful",
                    "user": {
                        "id": user.id,
                        "role": user.role,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "mobileno": user.mobileno,
                        "gender": user.gender,
                        "address": user.address,
                        "image": str(user.image)
                                }
                })

            else:

                return JsonResponse({
                    "success": False,
                    "message": "Invalid Password"
                })

        except User.DoesNotExist:

            return JsonResponse({
                "success": False,
                "message": "Email Not Found"
            })

    return JsonResponse({
        "success": False
    })

# =========================================
# LOGOUT API
# =========================================

def logout_api(request):

    logout(request)

    return JsonResponse({
        "success": True,
        "message": "Logout successful"
    })



# =========================================
# PROFILE API
# =========================================

@require_GET
def profile_api(request):

    # 1. AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "User Not Logged In"
        }, status=401)

    try:

        user = request.user

        # 2. SAFE IMAGE URL HANDLING
        image_url = None

        if getattr(user, "image", None):

            try:
                image_url = request.build_absolute_uri(
                    user.image.url
                )
            except (ValueError, OSError):
                image_url = None

        # 3. PROFILE RESPONSE
        return JsonResponse({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "mobileno": getattr(user, "mobileno", "") or "",
                "gender": getattr(user, "gender", "") or "",
                "address": getattr(user, "address", "") or "",
                "image": image_url
            }
        }, status=200)

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": f"Server Error: {str(e)}"
        }, status=500)


# =========================================
# UPDATE PROFILE API
# =========================================

@csrf_exempt
def update_profile_api(request):

    # 1. AUTHENTICATION CHECK
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Authentication Required. Please Login."
        }, status=401)

    # 2. REQUEST METHOD CHECK
    if request.method != "PUT":
        return JsonResponse({
            "success": False,
            "message": "PUT Method Required"
        }, status=405)

    try:

        # 3. READ JSON DATA
        try:
            data = json.loads(request.body or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({
                "success": False,
                "message": "Invalid JSON Data"
            }, status=400)

        if not isinstance(data, dict):
            return JsonResponse({
                "success": False,
                "message": "Invalid Request Data"
            }, status=400)

        # 4. GET LOGGED-IN USER
        user = request.user

        # 5. VALIDATE INPUT
        first_name = str(
            data.get("first_name", user.first_name) or ""
        ).strip()

        last_name = str(
            data.get("last_name", user.last_name) or ""
        ).strip()

        mobileno = str(
            data.get("mobileno", getattr(user, "mobileno", "")) or ""
        ).strip()

        gender = str(
            data.get("gender", getattr(user, "gender", "")) or ""
        ).strip()

        address = str(
            data.get("address", getattr(user, "address", "")) or ""
        ).strip()

        if not first_name:
            return JsonResponse({
                "success": False,
                "message": "First Name Is Required"
            }, status=400)

        if not last_name:
            return JsonResponse({
                "success": False,
                "message": "Last Name Is Required"
            }, status=400)

        if not mobileno.isdigit() or len(mobileno) != 10:
            return JsonResponse({
                "success": False,
                "message": "Mobile Number Must Be 10 Digits"
            }, status=400)

        if gender not in ["Male", "Female"]:
            return JsonResponse({
                "success": False,
                "message": "Invalid Gender"
            }, status=400)

        if not address:
            return JsonResponse({
                "success": False,
                "message": "Address Is Required"
            }, status=400)

        # 6. UPDATE USER FIELDS
        user.first_name = first_name
        user.last_name = last_name
        user.mobileno = mobileno
        user.gender = gender
        user.address = address

        # 7. SAVE DATABASE
        user.save()

        # 8. SUCCESS RESPONSE
        return JsonResponse({
            "success": True,
            "message": "Profile Updated Successfully"
        }, status=200)

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": f"Server Error: {str(e)}"
        }, status=500)


# =========================================
# IMAGE UPLOAD API
# =========================================

@csrf_exempt
def imageupload(request):

    try:

        # USER ID
        user_id = request.POST.get("user_id")

        # IMAGE FILE
        image = request.FILES.get("image")

        if not user_id:

            return JsonResponse({
                "success": False,
                "message": "User ID missing"
            })

        if not image:

            return JsonResponse({
                "success": False,
                "message": "Image missing"
            })

        # GET USER
        user = User.objects.get(id=user_id)

        # DELETE OLD IMAGE
        if user.image:

            old_image_path = user.image.path

            if os.path.isfile(old_image_path):

                os.remove(old_image_path)

        # SAVE NEW IMAGE
        user.image = image

        user.save()

        return JsonResponse({

            "success": True,

            "message": "Image uploaded successfully",

            "image_url": user.image.url

        })

    except Exception as e:

        print(e)

        return JsonResponse({

            "success": False,

            "error": str(e)

        })


# =========================================
# API Profile data view
# =========================================

def profile_api(request):

    if not request.user.is_authenticated:

        return JsonResponse({
            "success": False,
            "message": "User Not Logged In"
        })

    user = request.user

    return JsonResponse({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobileno": user.mobileno,
            "gender": user.gender,
            "address": user.address,
            "image": user.image.url if user.image else None
        }
    })

@csrf_exempt
def generate_unique_code_api(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    try:
        data = json.loads(request.body)

        issuername = data.get("issuername", "").strip()
        issuedto = data.get("issuedto") or None
        subject = data.get("subject") or None
        issuedate = data.get("issuedate") or None

        if not issuername:
            return JsonResponse({
                "success": False,
                "message": "Issuer name is required"
            }, status=400)

        if len(issuername) > 80:
            return JsonResponse({
                "success": False,
                "message": "Issuer name cannot exceed 50 characters"
            }, status=400)

        if issuedto and len(issuedto) > 80:
            return JsonResponse({
                "success": False,
                "message": "Issued-to name cannot exceed 80 characters"
            }, status=400)

        if subject and len(subject) > 300:
            return JsonResponse({
                "success": False,
                "message": "Subject cannot exceed 100 characters"
            }, status=400)

        if issuedate:
            try:
                datetime.strptime(issuedate, "%Y-%m-%d")
            except ValueError:
                return JsonResponse({
                    "success": False,
                    "message": "Invalid issue date"
                }, status=400)

        prefix = "PJKSS"
        current_year = datetime.now().year

        def create_code():
            return "".join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=10
                )
            )

        # Generate and save a unique code.
        # A transaction protects the database operation.
        with transaction.atomic():

            while True:
                code = f"{prefix}{current_year}{create_code()}"

                if not UniqueCode.objects.filter(code=code).exists():
                    break

            record = UniqueCode.objects.create(
                code=code,
                issuername=issuername,
                issuedto=issuedto,
                subject=subject,
                issuedate=issuedate or None
            )

        return JsonResponse({
            "success": True,
            "message": "Succesfully serial number Generated"
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON data"
        }, status=400)

    except Exception:
        return JsonResponse({
            "success": False,
            "message": "Unable to generate serial number"
        }, status=500)




# =========================================
# SEARCH SERIAL API
# =========================================

@csrf_exempt
def search_serial_api(request):

    code = request.GET.get("serialno")

    serial = UniqueCode.objects.filter(code=code).values()

    if serial.exists():

        return JsonResponse({
            "success": True,
            "data": list(serial)
        })

    return JsonResponse({
        "success": False,
        "message": "Serial not found"
    }, status=404)


# =========================================
# SERIAL LIST API
# =========================================

@csrf_exempt
def serial_list_api(request):

    serials = UniqueCode.objects.all().values()

    return JsonResponse({
        "success": True,
        "data": list(serials)
    })


# =========================================
# UPDATE SERIAL API
# =========================================

@csrf_exempt
def update_serial_api(request):

    if request.method != "PUT":
        return JsonResponse({
            "success": False,
            "message": "PUT method required"
        }, status=405)

    try:

        data = json.loads(request.body)

        code = data.get("serialno")

        serial = UniqueCode.objects.get(code=code)

        serial.issuedto = data.get("issuedto")
        serial.subject = data.get("subject")
        serial.issuedate = data.get("issuedate")
        serial.issuername = data.get("issuername")

        serial.save()

        return JsonResponse({
            "success": True,
            "message": "Serial updated successfully"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# =========================================
# DONATION LIST API
# =========================================

def donation_list_api(request):

    donations = donation.objects.all().values()

    # TOTAL AMOUNT
    total_amount = donation.objects.aggregate(
        total=Sum('Amount')
    )['total'] or 0

    return JsonResponse({
        "success": True,
        "data": list(donations),
        "total_amount": total_amount
    })


# =========================================
# LOGIN HISTORY API
# =========================================
# user loaction
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    geo = get_geo_info(ip)
    device = get_device_info(request)

    UserLoginInfo.objects.create(
        user=user,
        ip_address=ip,
        city=geo.get('city'),
        region=geo.get('region'),
        country=geo.get('country'),
        browser=device.get('browser'),
        os=device.get('os'),
        device=device.get('device')
    )


# =========================================
# HOME API
# =========================================

class HomeApi(View):

    def get(self, request):

        data = updates.objects.all().order_by('-id').values()

        return JsonResponse({
            "success": True,
            "updates": list(data)
        })


# Donation Qr Code API

@api_view(["POST"])
def donationdetail(request):

    try:

        # GET AMOUNT FROM REACT
        amount = request.data.get("amount")

        # VALIDATION
        if not amount:
            return Response(
                {
                    "success": False,
                    "message": "Amount is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # CREATE UPI LINK
        qr_text = (
            "upi://pay?"
            "pa=dhirajpatel08@okaxis"
            "&pn=DHIRAJ%20PATEL"
            f"&am={amount}"
            "&cu=INR"
            "&aid=uGICAgID1xJq5DA"
        )

        # GENERATE QR CODE
        qr_image = qrcode.make(qr_text, box_size=15)

        stream = BytesIO()

        qr_image.save(stream, format="PNG")

        qr_image_data = stream.getvalue()

        # CONVERT TO BASE64
        qr_image_base64 = base64.b64encode(
            qr_image_data
        ).decode("utf-8")

        # PHONEPE LINK
        upilinkPTM = (
            "https://mercury-uat.phonepe.com/transact/uat_v2?"
            "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        )

        # SEND RESPONSE TO REACT
        return Response(
            {
                "success": True,
                "amount": amount,
                "qr_image_base64": qr_image_base64,
                "upi_link": qr_text,
                "upilinkPTM": upilinkPTM
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:

        return Response(
            {
                "success": False,
                "message": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#Password rest email api views###


class PasswordResetAPIView(APIView):

    def post(self, request):

        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = (
                f"http://pjkss.com/"
                f"reset-password/{uid}/{token}/"
            )

            send_mail(
                'Password Reset',
                f'Click this link to reset password:\n{reset_link}',
                'yourgmail@gmail.com',
                [email],
                fail_silently=False,
            )

            return Response({
                'message': 'Password reset link sent successfully'
            })

        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class PasswordResetConfirmAPIView(APIView):

    def post(self, request):

        uid = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()

                return Response({
                    'message': 'Password changed successfully'
                })

            return Response({
                'error': 'Invalid token'
            }, status=400)

        except Exception:
            return Response({
                'error': 'Something went wrong'
            }, status=400)

#Password rest manually api views###

class ChangePasswordAPIView(APIView):

    def post(self, request):

        email = request.data.get("email")
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        try:

            user = User.objects.get(email=email)

            # CHECK OLD PASSWORD
            if not user.check_password(old_password):

                return Response({
                    "success": False,
                    "message": "Old password is incorrect"
                })

            # CHANGE PASSWORD
            user.set_password(new_password)
            user.save()

            return Response({
                "success": True,
                "message": "Password changed successfully"
            })

        except User.DoesNotExist:

            return Response({
                "success": False,
                "message": "User not found"
            })




#Vijya///////////////////////////////////////////////////////


# =========================================
# Create New Party Lst
# =========================================

@api_view(["GET", "POST"])
def party_list_create(request):

    # सभी पार्टियों की लिस्ट
    if request.method == "GET":
        parties = PartyDetail.objects.all().order_by("-id")
        serializer = PartyDetailSerializer(parties, many=True)
        return Response(serializer.data)

    # नई पार्टी सेव करना
    elif request.method == "POST":
        serializer = PartyDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Party saved successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



# =========================================
# Party Deail
# =========================================

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def party_detail(request, party_id):

    try:
        party = PartyDetail.objects.get(id=party_id)
    except PartyDetail.DoesNotExist:
        return Response(
            {"message": "Party not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # एक पार्टी की जानकारी
    if request.method == "GET":
        serializer = PartyDetailSerializer(party)
        return Response(serializer.data)

    # पार्टी अपडेट करना
    elif request.method in ["PUT", "PATCH"]:
        serializer = PartyDetailSerializer(
            party,
            data=request.data,
            partial=(request.method == "PATCH")
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Party updated successfully",
                "data": serializer.data
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # पार्टी डिलीट करना
    elif request.method == "DELETE":
        party.delete()
        return Response(
            {"message": "Party deleted successfully"},
            status=status.HTTP_200_OK
        )

# =========================================
# CREATE AND DISPLAY TAX INVOICES
# =========================================

@api_view(["GET", "POST"])
def tax_invoice_list_create(request):

    # GET: Display all invoices
    if request.method == "GET":

        invoices = TaxInvoice.objects.prefetch_related(
            "items"
        ).all()

        serializer = TaxInvoiceSerializer(
            invoices,
            many=True
        )

        return Response(serializer.data)

    # POST: Create new invoice
    if request.method == "POST":

        serializer = TaxInvoiceCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            invoice = serializer.save()

            response_serializer = TaxInvoiceSerializer(invoice)

            return Response(
                {
                    "success": True,
                    "message": "Invoice created successfully",
                    "invoice": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================
# GET SINGLE INVOICE
# =========================================

@api_view(["GET"])
def tax_invoice_detail(request, invoice_id):

    try:
        invoice = TaxInvoice.objects.prefetch_related(
            "items"
        ).get(id=invoice_id)

    except TaxInvoice.DoesNotExist:

        return Response(
            {"error": "Invoice not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TaxInvoiceSerializer(invoice)

    return Response(serializer.data)





from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .models import TaxInvoice, TaxInvoiceItem


# =========================================
# UPDATE INVOICE ITEMS ONLY
# CUSTOMER DETAILS WILL NOT BE MODIFIED
# DISCOUNT AFTER GST
# =========================================

@api_view(["PUT", "PATCH"])
def tax_invoice_update(request, invoice_id):

    try:

        with transaction.atomic():

            # =================================
            # GET EXISTING INVOICE
            # =================================

            invoice = get_object_or_404(
                TaxInvoice.objects.select_for_update(),
                id=invoice_id
            )

            # =================================
            # GET ITEMS FROM REACT
            # =================================

            items_data = request.data.get("items")

            if not isinstance(items_data, list) or not items_data:

                raise ValidationError(
                    "At least one invoice item is required."
                )

            retained_item_numbers = []

            # =================================
            # PROCESS EACH ITEM
            # =================================

            for index, item in enumerate(items_data):

                item_no = index + 1

                item_name = str(
                    item.get("item_name") or ""
                ).strip()

                if not item_name:

                    raise ValidationError(
                        f"Item name required in row {item_no}."
                    )

                try:

                    quantity = Decimal(
                        str(item.get("quantity", 0))
                    )

                    rate = Decimal(
                        str(item.get("rate", 0))
                    )

                    discount = Decimal(
                        str(item.get("discount", 0))
                    )

                    cgst_rate = Decimal(
                        str(item.get("cgst_rate", 0))
                    )

                    sgst_rate = Decimal(
                        str(item.get("sgst_rate", 0))
                    )

                except Exception:

                    raise ValidationError(
                        f"Invalid numeric value in row {item_no}."
                    )

                # =================================
                # VALIDATION
                # =================================

                if quantity <= 0:

                    raise ValidationError(
                        f"Invalid quantity in row {item_no}."
                    )

                if rate < 0 or discount < 0:

                    raise ValidationError(
                        f"Invalid rate or discount in row {item_no}."
                    )

                if cgst_rate < 0 or sgst_rate < 0:

                    raise ValidationError(
                        f"Invalid GST rate in row {item_no}."
                    )

                # =================================
                # SUBTOTAL
                # =================================

                subtotal = quantity * rate

                # =================================
                # GST ON FULL SUBTOTAL
                # =================================

                cgst = (
                    subtotal * cgst_rate / Decimal("100")
                )

                sgst = (
                    subtotal * sgst_rate / Decimal("100")
                )

                total_before_discount = (
                    subtotal + cgst + sgst
                )

                # =================================
                # DISCOUNT AFTER GST
                # =================================

                if discount > total_before_discount:

                    raise ValidationError(
                        f"Discount exceeds total amount in row {item_no}."
                    )

                total_amount = (
                    total_before_discount - discount
                ).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP
                )

                # =================================
                # CREATE OR UPDATE ITEM
                # =================================

                TaxInvoiceItem.objects.update_or_create(

                    invoice=invoice,

                    item_no=item_no,

                    defaults={

                        "item_name": item_name,

                        "hsn_code": item.get("hsn_code") or None,

                        "quantity": quantity,

                        "unit": item.get("unit") or "PCS",

                        "rate": rate,

                        "cgst_rate": cgst_rate,

                        "sgst_rate": sgst_rate,

                        "discount": discount,

                        # FINAL AMOUNT AFTER GST AND DISCOUNT
                        "total_amount": total_amount,
                    }
                )

                retained_item_numbers.append(item_no)

            # =================================
            # DELETE REMOVED ITEMS
            # =================================

            TaxInvoiceItem.objects.filter(
                invoice=invoice
            ).exclude(
                item_no__in=retained_item_numbers
            ).delete()

            # =================================
            # RETURN UPDATED INVOICE ITEMS
            # =================================

            updated_items = TaxInvoiceItem.objects.filter(
                invoice=invoice
            ).order_by("item_no")

            return Response(
                {
                    "message": "Invoice items updated successfully",

                    "invoice_id": invoice.id,

                    "serial_no": invoice.serial_no,

                    "items": list(
                        updated_items.values()
                    )
                },
                status=status.HTTP_200_OK
            )

    except ValidationError as e:

        return Response(
            {"error": e.detail},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:

        return Response(
            {
                "error": "Invoice item update failed",
                "details": str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )



#///////////////Tax invoice EMail Sending/////////////////////

@api_view(["POST"])
def send_invoice_email(request, invoice_id):

    try:

        invoice = get_object_or_404(
            TaxInvoice,
            id=invoice_id
        )

        # Get customer email from database
        customer_email = invoice.email

        if not customer_email:
            return Response(
                {"error": "Customer email address not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get generated PDF
        pdf_file = request.FILES.get("pdf_file")

        if not pdf_file:
            return Response(
                {"error": "Invoice PDF is missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if pdf_file.size > 10 * 1024 * 1024:
            return Response(
                {"error": "PDF file must be smaller than 10 MB."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if pdf_file.content_type != "application/pdf":
            return Response(
                {"error": "Only PDF files are allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create email
        email = EmailMessage(
            subject=f"Tax Invoice - {invoice.serial_no}",

            body=f"""
Dear {invoice.name or invoice.customer_name},

Please find attached your tax invoice.

Invoice Number: {invoice.serial_no}

Thank you for choosing AB Electrical Works.

Regards,
AB ELECTRICAL WORKS
Plot No 7 Narkra Bokaro Steel City
Bokaro Steel City 827014
Mob No : 9431378910. 7870865028. 6200919537
GSTIN NO : 201PEPS5760GIZR
""",

            from_email=settings.DEFAULT_FROM_EMAIL,

            to=[customer_email]
        )

        # Attach PDF
        email.attach(
            f"{invoice.serial_no}.pdf",
            pdf_file.read(),
            "application/pdf"
        )

        # Send email
        email.send(fail_silently=False)

        return Response(
            {
                "success": True,
                "message": "Invoice email sent successfully.",
                "email": customer_email
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:

        return Response(
            {
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )