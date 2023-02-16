from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist       
from django.contrib.auth.decorators import login_required    
#Create your views here.
#nombre de la pagina al final del template

#sesion del usuario actual privada, por eso solo una _
#la funcion la uso en crear carrito 
#en el try si no existe la sesion la crea, si existe la retorna
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


#ESTA FUNCION HABIA DEJADO DE FUNCIONAR CUANDO MODIFICAMOS LO DE AGREGAR AL CARRITO Y INICIAR SESION, SE TUVO QUE MDOFICIAR
#todo esto se agrega en urls.py para que funcione
#crear carrito de compras
#Si el cart no existe lo creará en la base de datos
#sumar producto por cantidad en el carrito en cart.html con el simbolo (+)
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    #Este if fue agregado al final para la logica del carrito al comprar antes del login y arreglar los errores que daba
    current_user = request.user
    #Agregaré la logica del carrito cuando el usuario este dentro de la sesion
    #Tuve que copiar toda la funcion dentro del if y cambiar cart=cart por user=current_user
    if current_user.is_authenticated:
        
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
            
                try:                          
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
  


        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
  
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()


        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )   

            if len(product_variation) > 0:

                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
                cart_item.save()

        return redirect('cart')
        

    #AQUI VA TODA LA FUNCION NORMAL
    else:        
        product_variation = []
    #Este if es para capturar el valor del color
    #key = color, value = verde/rojo/azul, etc
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                #Después todo esto lo agrego al cart_item en el try de abajo
                #Estre try es para confirmar si existe el color
                try:                                                  #dos __ cuando llamas un operador
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    #Aqui le agrego el producto encontrado que es la variable variation
                    product_variation.append(variation)
                except:
                    pass


        #Crear carrito de compras
        try:
            cart = Cart.objects.get(cart_id= _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()


        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        #Agregar un elemento al carrito de compras
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            ex_var_list = []
            id = []
            #Con este for llenaré las listas de arriba para usarlos en el if de abajo
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            #Esto ocurre solo cuando la variacion del producto existe en la base de datos
            #Por ejemplo sumara las poleras con las mismas variaciones dentro del carrito
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            #Sino se repiten las variaciones creara otro producto en el carrito por separado
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                #Este if lo agregue para agregar las variations
                if len(product_variation) > 0:
                #Esto limpiara los variations anteriores para agregar los nuevos
                    item.variations.clear()
                    #Para que se agregue una coleccion lleva un * por delante
                    item.variations.add(*product_variation)
                item.save()


        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )   
            #Este if lo agregue para agregar las variations
            if len(product_variation) > 0:
                #Limpiamos primero antes de hacer cualquier cosa
                cart_item.variations.clear()
                    #Al ser una coleccion lo que agregare debe llevar un *
                cart_item.variations.add(*product_variation)
                cart_item.save()

        return redirect('cart')


#Esto tuvo que ser editado para evitar el error del login, se agrego el primer if y else
#Eliminar producto por cantidad en el carrito en cart.html con el simbolo (-)
def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id = product_id)


    try:
        #Esto fue agregado para evitar el error
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)        
        
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            #Esto estaba antes pero fue movido hasta aqui
            cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)

        #si la cantidad de productos es mayor a 1, lo irá borrando en 1 cada vez que le de al boton - en el carrito
        if cart_item.quantity>1:
            cart_item.quantity -= 1
            cart_item.save()
        
        #en el caso de que haya solo 1 producto, lo eliminará del carrito
        else:
            cart_item.delete() 
    except:
        pass
    
    return redirect('cart')


#Esto tambien fue modificado por el tema del login que después empezo a dar error, se agrego el if y se movieron algunas cosas
#Elimina un producto completo, sin importar la cantidad en el carrito en cart.html con el boton eliminar
def remove_cart_item(request, product_id, cart_item_id):
    #product se queda aqui
    product = get_object_or_404(Product,id=product_id)
    
    #Esto fue creado después
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user = request.user, id=cart_item_id)

    else:
        #Esto fue movido al ese
        cart = Cart.objects.get(cart_id=_cart_id(request)) 
        cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)

    #Esto se mantiene aqui
    cart_item.delete()
    return redirect('cart')





#Muestra la información del carrito de compras
def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        #Con este if hago que se muestre el carrito actualizado
        #al agregar un producto sin iniciar sesion y despues iniciarla
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            #get el cart por el id
            cart = Cart.objects.get(cart_id=_cart_id(request))
            #Aqui filtro por la variable cart de arriba(el segundo cart)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            #+= se irá sumando con cada for
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        #impuesto de 2%
        tax = (2*total)/100
        #total precio final
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass ## pass solo ignora la excepcion

#Esto es un dictionary que definira que valores quiero enviar al template
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,

    }
    return render(request, 'store/cart.html', context)

#login obligatorio para ir a checkout
#Esto es para mostrar lo mismo de arriba, todo el contenido de cart, solo habia que copoar
@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        #Con este if hago que se muestre el carrito actualizado
        #al agregar un producto sin iniciar sesion y despues iniciarla
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            #get el cart por el id
            cart = Cart.objects.get(cart_id=_cart_id(request))
            #Aqui filtro por la variable cart de arriba(el segundo cart)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            #+= se irá sumando con cada for



        #+= se irá sumando con cada for
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        #impuesto de 2%
        tax = (2*total)/100
        #total precio final
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass ## pass solo ignora la excepcion

#Esto es un dictionary que definira que valores quiero enviar al template
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,

    }
    return render(request, 'store/checkout.html', context)
