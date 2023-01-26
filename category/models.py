from django.db import models
from django.urls import reverse

# Create your models here.


#slug está destinado a estar dentro de la parte final de la url que representa a la entidad
#blank = true   permite valores nulos
#unique = que no se repita el valor
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    slug = models.CharField(max_length=100, unique=True)
    cast_image = models.ImageField(upload_to = 'photos/categories', blank=True)


#Cambiar el nombre dentro de la pagina admin ya que siempre coloca una s al final
#y con esto se arregla para que quede mejor
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    #llamo products_by_category de store/urls       #self representa categoria y le paso el valor de slug
    def get_url(self):
        return reverse('products_by_category', args=[self.slug])
    #get_url creará la url y le agregará el slug al final para que al hacer click en alguna categoria me redirige

    def __str__(self):
        return self.category_name
