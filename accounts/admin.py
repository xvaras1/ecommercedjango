from django.contrib import admin
from .models import Account, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

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

#Con esta claro hago la vista del user profiles en la pagina admin
#O como quiero que se vea mejor dicho
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        #format_html se debe importar
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url)) 

    thumbnail.short_description = 'Imagen de perfil'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')


# Register your models here.

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

