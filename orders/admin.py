from django.contrib import admin
from .models import Payment, Order, OrderProduct



class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price','ordered')
    extra = 0




class OrderAdmin(admin.ModelAdmin):
    #En la pagina de admin, las order mostraran estos datos
    list_display = ['order_number', 'full_name', 'phone', 'email','city','order_total','tax','status','is_ordered','created_at']
    #Los filtros que se mostraran en la pagina de admin
    list_filter = ['status', 'is_ordered']
    #Agregar un buscador en la pagina de admin con estos datos
    search_fields = ['order_number','first_name','last_name','phone','email']
    #Cuantos resultados tendrá una pagina en admin
    list_per_page = 20
    #Con esto incluyo la clase de arriba, esto me ayudará a mostrar los datos en una tabla en la pagina Admin/Orders
    inlines = [OrderProductInline]






# Register your models here.
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)


