from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Follow


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "email")
    search_fields = ("username",)
    list_filter = ("username", "email")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "author")
