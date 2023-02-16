from .models import Cart, CartItem
from .views import _cart_id

#Esta funcion la usaré en el template navbar
#Funcion para la suma total de productos agregados al carrito para poder mostrarla
#Esto se hace de forma global, asi que se debe agregar a settings/templates en ecommerce
def counter(request):
    cart_count = 0

    try:
        #Traer id del carrito
        cart = Cart.objects.filter(cart_id=_cart_id(request))
            #Con este if hago que se cuente la cantidad de productos al comprarlos y despues
            #iniciar sesion, tambien fue necesario modificar carts en views.py
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user=request.user)
        else:
            cart_items = CartItem.objects.all().filter(cart=cart[:1])

        for cart_item in cart_items:
            cart_count += cart_item.quantity
    
    except Cart.DoesNotExist:
        cart_count = 0
    
    return dict(cart_count=cart_count)
