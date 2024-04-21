from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from authentication.models import User


class UserModelAdmin(BaseUserAdmin):

    # The fields to be used in displaying the User model.

    list_display = ["id","email", "name", "tc", "is_admin"]
    list_filter = ["is_admin"]    
    search_fields = ["email"]
    ordering = ["email","id"]
    filter_horizontal = []


# Now register the new UserAdmin...
admin.site.register(User, UserModelAdmin)
