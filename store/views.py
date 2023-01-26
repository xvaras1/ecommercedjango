from django.shortcuts import render, get_object_or_404
from .models import Product
from .models import Category

# Create your views here.

#asi estaba antes
#def store(request):
#    return render(request, 'store/store.html')

def store(request, category_slug=None):
    categories = None
    products = None

    #si category_slug es diferente de none, osea que tiene un valor
    if category_slug != None:
        #si encuentra la categoria lista la coleccion, sino dará una excepcion 404
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:

        #llamar todos los productos disponibles
        products = Product.objects.all().filter(is_available=True)
        #esto es para que me devuelva la cantidad de productos en total de la base de datos
        product_count = products.count()


    #los valores de arriba los guardo en un dictionary
    context = {
        'products': products,
        'product_count': product_count,
    }

    
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    #hago un try para evitar que busque un producto que no exista y de error
    try:
                                        #lleva 2 _ _ para obtener el valor del campo de la tabla category
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
    }

    return render(request, 'store/product_detail.html', context)