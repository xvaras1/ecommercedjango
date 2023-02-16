from django.contrib import admin
from .models import Product, Variation, ReviewRating
#Aqui llamo los modelos de models.py

#Con estas clases cambiare la vista de productos u otra cosa en la pagina admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price','stock','category','modified_date','is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    #Cuando es solo uno, debe llevar , al final o dará error
    list_editable = ('is_active',)
    list_filter = ('product','variation_category', 'variation_value', 'is_active')


#Aqui registro los modelos y las clases de arriba
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)