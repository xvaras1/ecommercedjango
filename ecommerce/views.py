from django.shortcuts import render
from store.models import Product
""" render renderiza/desplega el codigo html """

#ASI ERA ANTES
#def home(request):

    #return render(request, 'home.html')


#Llamar todos los productos y filtrar solo los que estan disponibles
def home(request):
    products = Product.objects.all().filter(is_available=True)
    
    #Guardar lo que llamo en un dictionary
    context = {
        'products': products,
    }
    
    return render(request, 'home.html', context)