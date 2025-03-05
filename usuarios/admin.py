from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado,UserActivityLog

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff', 'login_attempts', 'fecha_creacion')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-fecha_creacion',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono')
        }),
        ('Roles y Permisos', {
            'fields': (
                'rol', 
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            )
        }),
        ('Auditoría', {
            'fields': ('last_login', 'date_joined', 'fecha_creacion')
        }),
         ('Seguridad', {
            'fields': (
                'login_attempts', 
                'last_login_ip', 
                'must_change_password'
            )
        }),
    
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'password1', 
                'password2', 
                'rol', 
                'is_staff', 
                'is_active'
            ),
        }),
    
    
    )

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'ip_address')
    ordering = ('-timestamp',)
    readonly_fields = ('user', 'activity_type', 'timestamp', 'ip_address', 'user_agent')

admin.site.register(UsuarioPersonalizado, CustomUserAdmin)