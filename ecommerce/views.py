from django.shortcuts import render
from store.models import Product, ReviewRating
""" render renderiza/desplega el codigo html """

#ASI ERA ANTES
#def home(request):

    #return render(request, 'home.html')


#Llamar todos los productos y filtrar solo los que estan disponibles
def home(request):                                      #Ordenado por fecha de creación
    products = Product.objects.all().filter(is_available=True).order_by('-create_date')

    #Con este for obtengo las reseñas de los productos para enviarlas al home a través del context
    for product in products:
        reviews = ReviewRating.objects.filter(product_id = product.id, status=True)
    
    #Guardar lo que llamo en un dictionary
    context = {
        'products': products,
        'reviews': reviews,
    }
    
    return render(request, 'home.html', context)