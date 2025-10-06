from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	search_fields = ('name',)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	ordering = ('email',)
	list_display = ('email', 'name', 'role', 'is_staff')
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(_('Personal info'), {'fields': ('name', 'role')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		(_('Important dates'), {'fields': ('last_login',)}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'name', 'password1', 'password2'),
		}),
	)
