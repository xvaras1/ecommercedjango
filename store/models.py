from django.db import models
from category.models import Category
from django.urls import reverse

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

    