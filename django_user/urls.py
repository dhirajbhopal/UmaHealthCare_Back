from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
#from django.contrib.auth import views
from core import urls as core_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views
from django.core.mail import send_mail, BadHeaderError
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # new
from django.views.static import serve #new
from django.urls import path, include, re_path #new
from core.views import Signup, PasswordResetAPIView, PasswordResetConfirmAPIView, ChangePasswordAPIView, HomeApi
from core import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('api/login/', views.login_api),
    path('HomeApi/',HomeApi.as_view(),),
    path('', include('core.urls')),
    path('imageupload/',views.imageupload,name='imageupload'),
    path('api/password-reset/', views.PasswordResetAPIView.as_view(), name='password_reset'),
    path('api/reset-password/', views.PasswordResetConfirmAPIView.as_view(), name='reset-password'),
    path('api/change-password/',views.ChangePasswordAPIView.as_view(),),
    path('signup/',Signup.as_view(),name='Signup'),
    path("sendotp_api/",views.sendotp_api,name="sendotp_api"),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
 
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)