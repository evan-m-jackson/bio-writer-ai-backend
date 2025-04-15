from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, FieldChoices, UserFields, UserAchievements, UserBio

@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'created_at', 'modified_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    list_filter = ('created_at', 'modified_at')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Timestamps', {'fields': ('created_at', 'modified_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

@admin.register(FieldChoices)
class FieldChoicesAdmin(admin.ModelAdmin):
    list_display = ('field',)
    search_fields = ('field',)

@admin.register(UserFields)
class UserFieldsAdmin(admin.ModelAdmin):
    list_display = ('user', 'field', 'order_num', 'years')
    list_filter = ('field',)
    search_fields = ('user__email', 'field__field')

@admin.register(UserAchievements)
class UserAchievementsAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievements')
    search_fields = ('user__email', 'achievements')

@admin.register(UserBio)
class UserBioAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email', 'bio')
