from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Resource."""

    list_display = ('pk', 'email','first_name', 'last_name','mobile_number','is_staff')
    list_display_links = ('pk','email')
    # list_editable = ()

    search_fields = (
        'first_name',
        'last_name',
        'email',
    )

    list_filter = (
        'email',
        'is_staff',
    )
