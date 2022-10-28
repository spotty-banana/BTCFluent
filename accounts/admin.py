from django.contrib import admin

from .models import Account
from .models import Asset

# Register your models here.


# disable "delete selected" action in django admin
admin.site.disable_action('delete_selected')


class Admin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    list_display_links = None


# register items and admins

admin.site.register(Account, Admin)
admin.site.register(Asset, Admin)
