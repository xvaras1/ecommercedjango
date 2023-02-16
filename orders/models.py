from django.db import models
from accounts.models import Account
from store.models import Product, Variation


#LOS MODELOS SE REGISTRAN EN admin.py

# Create your models here.

class Payment(models.Model):
                                      #Si elimino un usuario tambien se debe eliminar el registro de Payment
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):


        return self.payment_id



class Order(models.Model):
    #Diccionario para usarlo en status
    STATUS = (
        ('New', 'Nuevo'),
        ('Accepted', 'Aceptado'),
        ('Completed', 'Completado'),
        ('Cancelled', 'Cancelado'),
    )
                            #Clave secundaria de Account
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
                            #Clave secundaria de Payment
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    addres_line_1 = models.CharField(max_length=100)
    addres_line_2 = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
                        #floatfield porque es probable que sea decimal
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #Estas dos funciones las usaré para devolver los dos nombres juntos en el template para evitar atados
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.addres_line_1} {self.addres_line_2}'


    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
                   #Clave secundaria de Orden 
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product.product_name

