from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
#esta libreria ayuda a la paginacion de una pagina
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
#Esto ayudará a la busqueda de productos
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct


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
        #aqui pegue paginator, page, paged_products que estaban en el else, así evito un error en el catalogo
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 5)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:

        #llamar todos los productos disponibles
        products = Product.objects.all().filter(is_available=True).order_by('id')
        #Aqui hago la paginacion de productos en grupos de 5
        paginator = Paginator(products, 5)
        #Con esta forma ya se a que pagina quiere acceder el cliente(paginacion)
        page = request.GET.get('page')
        #Esto representará los 5 productos
        paged_products = paginator.get_page(page)
        #esto es para que me devuelva la cantidad de productos en total de la base de datos
        product_count = products.count()


    #los valores de arriba los guardo en un dictionary
    #Aqui lo cambie y le agregé el paged_products, antes era solo products
    context = {
        'products': paged_products,
        'product_count': product_count,
    }

    
    return render(request, 'store/store.html', context)



def product_detail(request, category_slug, product_slug):
    #hago un try para evitar que busque un producto que no exista y de error
    try:
                                        #lleva 2 _ _ para obtener el valor del campo de la tabla category
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        #en caso de que exista el producto dentro del carrito de compras al comprarlo nuevamente, será true
        #aqui uso la funcion _cart_id de carts.views y CartItem de carts.models
        #Esto lo usaré en product_detail.html
        in_cart =CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    #Con este if arreglo los errores que me daba el try   
    if request.user.is_authenticated:
        #Este try lo agregue para que un usuario pueda reseñar solo cuando haya comprado el producto
        #Primero empiezo con esto y el orderproduct lo coloco en el context para trabajarlo agregando una condicion en el template product_detail.html
        try:
            #Si existe significa que el cliente ha comprado este producto
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    #Con esto llamo todas las reviews de un producto en especifico y lo envio al context para enviarlo al html
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews':reviews,
    }

    return render(request, 'store/product_detail.html', context)

#Funcion de busqueda de productos, que usaré en navbar donde se encuentra el buscador
def search(request):
    #Quiero tener este parametro desde la url que me envie el cliente
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        #Si la palabra existe
        if keyword:
            #Ordernar segun fecha de creacion de forma descendiente -
            #Buscar producto si concuerda con el nombre o la descripcion en filter
            #Para buscarlo uso la herramienta importada llamada Q       #Si la descripcion contiene la palabra buscada
            #EN DJANGO EN VEZ DE USAR OR, SE USA | la barrita
            products = Product.objects.order_by('-create_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            #Aqui la cantidad de productos que me devuelve
            product_count = products.count()
    
    #Aqui el dictionary con los valores que enviare al template store
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render (request, 'store/store.html', context)



def submit_review(request, product_id):
    #Con esto capturo la url
    url = request.META.get('HTTP_REFERER')
    #Si el envio de datos es de tipo POST
    if request.method == 'POST':
        try:
            #Con esto llamo el review del usuario y del producto a través del id
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            #Con esto capturo los valores dentro de form
            #Si este review existe, lo actualizaré
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Tu comentario ha sido actualizado')
            return redirect(url)
        #Si la review no existe la crearé desde cero con todo esto    
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            #Si el formulario es valido, se guardará en la t abla ReviewRating
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Muchas gracias, tu comentario fue enviado con exito!')
                return redirect(url)
