from django.db import models
from store.models import Product, Variation
from accounts.models import Account

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

#ManyToManyField almacena una coleccion de data
#EL user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True) lo agregue
#Para cuando agrego un item al carrito sin sesion y después me logeo, los items se mantengan
#Esto ayudará pero después hay que programarlo para que asi funcione en accounts/views
class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    #para evitar el error de __str__ coloco __unicode__
    def __unicode__(self):
        return self.product

#CADA VEZ QUE ACTUALICES UN MODELO HAY QUE HACER UN makemigration y migrate