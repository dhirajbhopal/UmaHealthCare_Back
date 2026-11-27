from django.contrib import admin
#from student.models import student
#from faculty.models import faculty
from core.models import User,UserLoginInfo
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("username", "email", "masked_password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "role", "image", "address" ,"mobileno", "gender")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    list_display = ("email", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions",)
    readonly_fields = ("masked_password", "email", "username")

    def masked_password(self, obj):
        """Show password as stars in admin panel (safe, doesn't expose actual hash)."""
        if not obj.password:
            return ""
        # You can use a fixed number of stars or match length of hash
        return format_html('<span style="letter-spacing:2px;">{}</span>', '*$#' * 20)
    masked_password.short_description = "Password"



"""@admin.register(UniqueCode)
class UniqueCodeAdmin(admin.ModelAdmin):
    list_display=['code','issuername','issuedto','subject','issuedate']"""

