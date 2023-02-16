from django.shortcuts import render, redirect
#Esto es para trabajar con json, lo uso en payments, en su return al final
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from store.models import Product
#Estas dos liibrerias las uso para poder enviar un correo
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
#El json lo importo para trabajar con la función payments
import json


# Create your views here.

def payments(request):
    body = json.loads(request.body)
    #Con esto consigo los datos de la orden de paypal
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method =body['payment_method'],
        amount_id = order.order_total,
        status = body['status'],
    )
    payment.save()

    #Al tener order un objeto payment como foreignkey, le seteo payment
    order.payment = payment
    #Con esto cambio esto de false a true
    order.is_ordered = True
    order.save()

    #Mover todos los carrito items hacia la tabla order product, para programar el tema de stock
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        #Esto es para guardar los variations de los productos comprados en la tabla Order products
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #Con esto disminuyo el stock cuando se hace una compra
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()

    #Esto limpia el carrito después de hacer una compra
    CartItem.objects.filter(user=request.user).delete()

    #Cuerpo del email de recibo de compra
    mail_subject = 'Gracias por tu compra'
    body = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    #A quien va dirigido el email, en este caso al cliente
    #Con esto guardo la informacion del correo del usuario actual en la compra
    to_email = request.user.email
    #Aqui lo envio a ese correo
    send_email = EmailMessage(mail_subject, body, to=[to_email])
    send_email.send()

    #Esta información la usaré en json para el url de redireccionamiento
    #Además de que esto también lo trabajo en orders/payments.html en la parte de json
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)






#Crear orden de compra
def place_order(request, total=0, quantity=0):
    current_user = request.user
    #Con esto llamo a todos los productos que tiene el usuario actual
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    #Si lo hay elementos que comprar te redireccionará a store
    if cart_count <=0:
        return redirect('store')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
                    #Multiplico el precio del producto por la cantidad
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    #Este es el impuesto del 2%
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
                #Llamo a OrderForm de forms.py
        form = OrderForm(request.POST)

        #Si el formulario es valido creará el orden de compra
        if form.is_valid():
                  #Creando orden de compra
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.addres_line_1 = form.cleaned_data['addres_line_1']
            data.addres_line_2 = form.cleaned_data['addres_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
                     #Con esto consigo la ip, funcion de python
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #Al guardar, se genera un id automaticamente que usaré abajo

            #Conseguir fecha actual, año, mes y dia
            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            
            d = datetime.date(yr,mt,dt)
        #Con esto cambia la forma de imprimir la fecha
            current_date = d.strftime("%Y%m%d")
        #Con esto junto el current_date y el id de la compra que se genera automaticamente
        #Con esto evite que no de problemas al repetirse el current_date en una compra, ya que lo junto con el id
            order_number = current_date + str(data.id)
            data.order_number = order_number
            #Con esto actualizo el dato
            data.save()

            #Con esto llamo la orden creadara para usarla en el render al redireccionar y enviar el diccionario con los datos al payments 
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }

            return render(request, 'orders/payments.html', context)

    else:
        return redirect('checkout')



#Mostrar resultados de orden de compra
def order_complete(request):
    #Aqui obtengo los datos que yo coloque en la url de la orden de compra
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        #Aqui llamo toda la informacion de order por order_number de la compra y si is_ordered es igual a TRUE
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        #Aqui llamo la informacion de  OrderProduct filtrado por el id de la compra
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        #Con este bucle llamo los datos de ordered_products
        for i in ordered_products:
            subtotal += i.product_price*i.quantity
        #Aqui llamo los objetos de la tabla Payment segun el id de la compra
        payment = Payment.objects.get(payment_id = transID)

        #Este diccionario llamo y guardo la informacion de varias tablas para enviarlas a order_complete.html y llamarla ahi
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context) 
    
    #En caso de que haya error te llevará al home
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')


