from django.contrib import admin

from .models import Follow


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name")
    list_filter = ("username", "email")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
