from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin

class AccountAdmin(UserAdmin):
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    #que sea solo de lectura
    readonly_fields = ('last_login','date_joined')
    #ordenar de forma ascendente segun la fecha
    ordering = ('-date_joined',)
    #debe llevar coma al final -date_joined para que no de error

    filter_horizontal=()
    list_filter=()
    fieldsets=()



# Register your models here.

admin.site.register(Account, AccountAdmin)

