from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
#Libreria para obtener el promedio
from django.db.models import Avg, Count
# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    product_name = models.CharField(max_length=200, unique=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    #Cuando se elimine una categoria, tambien se eliminaran los productos relacionados usando CASCADE
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    #auto_now_add Es solo para agregar la fecha de creacion la primera vez
    create_date = models.DateTimeField(auto_now_add=True)
    #auto_now la fecha se se modificara cada vez que se modifique un producto y se guarde
    modified_date = models.DateTimeField(auto_now=True)

    #Esta funcion la implemento en home para que al hacer un click en un producto me redirige a su pagina de detalles
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])


    #Listar los productos por un nombre/label especifico, aqui uso product_name
    def __str__(self):
        return self.product_name

    #Con esto obtengo el promedio del puntaje de las reseñas, avg se importa para usarla
    #La funcion la uso en product_detail.html
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])  
        return avg 

    #Con esta funcion obtengo la cantidad total de reseñas para mostrarlas en un numero, count se importa para usarlo
    #La funcion la uso en product_detail.html
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count=0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

#Aqui separo color y talla para que en el template product_detail no muestre todo junto y asi arreglarlo
#debo colocar objects = VariationManager() dentro de la clase 'Variation' para que esta clase funcionen
class VariationManager(models.Manager):
    def color(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def tallas(self):
        return super(VariationManager, self).filter(variation_category='talla', is_active=True)


variation_category_choice = (
    ('color', 'color'),
    ('talla', 'talla'),
)

#Al usar choice en variation_category primero lo defino arriba
#Este modelo será para la seleccion de variaciones de productos

class Variation(models.Model):
    #product es una clase foranea que viene de arriba
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices = variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()


    #Listar variations de un producto con respectivo valor
    def __str__(self):
        return self.variation_category + ':' + ' ' + self.variation_value

#LOS MODELOS SE REGISTRAN EN ADMIN.PY


#Reseñas de clientes
class ReviewRating(models.Model):
                                #Si se elimina un producto, tambien las reseñas
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject