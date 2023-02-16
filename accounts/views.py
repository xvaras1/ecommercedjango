from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserProfileForm, UserForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage 
from orders.models import Order 
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

# Create your views here.

def register(request):
    #registrationform lo llamo de forms.py y ahora lo llamo en una variable form
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        #Si es formulario es valido
        if form.is_valid():
            #en estas variables guardo la informacion que me envie el cliente
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            #split separa el @ del email y separa x partes, en este caso, solo la parte antes del @, eso es el username
            username = email.split('@')[0]
            #llamamos el funcion create user de models.py, para crear la instancia del usuario 'user'
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            #este dato y los de arriba es para el model Account
            user.phone_number = phone_number
            user.save()

            #Ahora es obligatorio esto, ya que al crear una cuenta, se debe crear un perfil automaticamente con esto
            #Cuando el usuario se cree una cuenta, con esto se creará un perfil por defecto con estos datos
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()



            
            current_site = get_current_site(request)
            #Titulo del correo electronico a enviar para activacion
            mail_subject = 'Por favor, active su cuenta en Vaxi Drez'
            #El contenido del correo será un html
            body = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
                #COMPARTIR PRIMARY KEY ES PELIGROSO, HAY QUE CIFRARLA (uid)
            #Con esto envio el email con todo su contenido
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()
            #Todo esto se importará arriba from django

            #importo messages para usarlo
            #messages.success(request, 'Registrado exitosamente')
            #Al registrar te redireccionará al login y enviará una verificacion de email
            return redirect('/accounts/login/?command=verification&email='+email)

    #Dictionary que guardara los datos de registro
    context = {
        'form': form
    }
    return render (request, 'accounts/register.html', context)

#Esto también fue modificado para arreglar el error del carrito por la fusion del carrito por el tema de comprar sin login y con
def login(request):
    #Los datos que recibirá del cliente si es post
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
              #El auth se importa en la parte superior
        user = auth.authenticate(email=email, password=password)

        #Si el usuario no es nulo que haga un login
        if user is not None:

            try:
                #Esto hace que al registrar un producto sin un usuario y después hagas login
                #Manteniendo los producto dentro del login
                #Después tuve que editar context_proccesors en carts para que el contador de productos se actualice
                #y por ultimo fue necesario modificar carts en carts/views para que se actualice la vista del carrito
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    #Esto y el for fue agregado por el tema de comprar sin login y las variaciones se compren por separado    
                    #LISTA 1
                    product_variation = []
                    #Con esto tengo las variaciones de productos que se registraron sin sesion
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #Aqui las variaciones que fueron registrados cuando el usuario estaba en sesion    
                    cart_item = CartItem.objects.filter(user=user)  
                    #LISTA 2
                    ex_var_list = []
                    id = []  
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    #Esto solo va a ocurrir cuando haya coincidencia en las variaciones de la lista 1 y 2
                    #Y esto lo arregla al final, en vez de crear otro producto con mismas variaciones, lo sumará ahora
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()

                        #En caso de que no haya coincidencias simplemente le agregará un usuario al item 
                        else:
                            cart_item =CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

                    #Esto fue borrado y reemplazado por lo de arriba
                   # for item in cart_item:
                   #    item.user = user
                   #    item.save()
            except:
                pass
            #Con el next haré que al comprar sin usuario y dar a pagar, te lleve a logearte, yal logearte te lleve a esa pagina
            #Para que esto funcione se debe instalar la libreria pip install requests    y despues importarla
            #http://localhost:8000/accounts/login/?next=/cart/checkout/
            auth.login(request, user)
            messages.success(request, 'Has iniciado sesión exitosamente')
            #Esta es la futura url de arriba
            url = request.META.get('HTTP_REFERER')

            try:
                #Aqui le paso a la variable toda la url de arriba
                query = requests.utils.urlparse(url).query
                #Con esto capturaria todo el valor de next de la url de arriba
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                #Y aqui normalmente al logear te llevará a home
                return redirect('home')


        else:
            messages.error(request, 'El usuario ingresado es incorrecto')
            return redirect('login')



    return render (request, 'accounts/login.html')


#@login_required hace que para cerrar sesion sea obligatorio estar en una sesion, esto se importa de arriba
@login_required(login_url='login')
def logout(request):
    #La funcion ya está lista con auth  
    auth.logout(request)
    messages.success(request, 'Has cerrado la sesión')

    return redirect('login')
#funcion de cerrar sesion



#Esta funcion hará su funcion cuando el cliente haga click en el link de activacion en su correo
#Funcion de activacion/verificacion de cuenta
def activate(request, uidb64, token):
    try: 
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicidades, tu cuenta ha sido activada!')
        return redirect('login')
    else:
        messages.error(request, 'La activacion fue erronea')
        return redirect('register')


#Funcion de enviar correo para resetear contraseña
@login_required(login_url='login')
def dashboard(request):
    #En esta variable llamo las ordenes por su usuario y que hayan sido ordenadas
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    #Aqui cuento las ordenes que llame arriba
    orders_count = orders.count()
    #Aqui guardo el contador de ordenes en un dictionary para enviarlo en el return
    
    #Con esto consigo el userprofile, CON ESTO ENVIO LA FOTO AL TEMPLATE DASHBOARD,
    #, aparte de todos los datos del respecto userprofile, después lo paso al context para que se envie
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)




def forgotPassword(request):
    if request.method == 'POST':
        #Aqui guardo el correo que me envio el cliente
        email = request.POST['email']
        #El correo enviado existe?
        if Account.objects.filter(email=email).exists():
            #Con esto tengo el usuario de la base de datos si es que existe
            user = Account.objects.get(email__exact=email)

            #Correo a enviar para cambiar contraseña
            current_site = get_current_site(request)
            mail_subject = 'Cambiar contraseña'
            body = render_to_string('accounts/reset_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()
 
            messages.success(request,'Te hemos enviado un correo para cambiar tu contraseña')
            return redirect('login')

        #En caso de que el usuario no exista
        else:
            messages.error(request, 'La cuenta de usuario no existe')
            return redirect('forgotPassword')


    return render(request, 'accounts/forgotPassword.html')


#Esta funcion es para obtener datos y validar cuando el cliente le de click al link
#de reset password
def resetpassword_validate(request, uidb64, token):
    #Este metodo es para capturar el uid, el parametro codificado y el user
    #Cuando el cliente haga click al link
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    #Si al procesar el link detecto que el usuario y el token es correcto y existen
    #Me llevará al formulario resetPassword
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor resetea tu contraseña')
        return redirect('resetPassword')
    else:
        messages.error(request, 'El link ha expirado')
        return redirect('login')

#Con esta funcion reseteo la contraseña con el html resetPassword
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        #Si password es igual a confirm_password
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'El password ha sido cambiado correctamente')
            return redirect('login')
        else:
            messages.error(request, 'El password no coincide')
            return redirect('reset_Password')
        
    else: 
        return render(request, 'accounts/resetPassword.html')


#Con esto busco enviar una lista de ordenes del usuario en el dashboard/my_orders
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }

    return render(request, 'accounts/my_orders.html', context)

#Aqui hago todo para poder editar un perfil de usario, llamo el UserProfile y UserProfileForm de forms.py
@login_required(login_url='login')
def edit_profile(request):
    #Con esto obtengo el perfil de usuario, el UserProfile se debe importar 
    userprofile =  get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
                    #El UserForm se importa de forms.py
        user_form = UserForm(request.POST, instance=request.user)
        #Al pedir foto debo colocar request.FILES y el userprofile es una variable que viene de arriba
        #Con esto obtengo el profile_form, UserProfileForm se importa de forms.py
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        #Cuando el cliente rellene los datos de editar perfil y los dos formularios sean validos
        #Se guardará
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Su información ha sido guardada')
            return redirect('edit_profile')
    else:
        #Con esto llamo los datos de los dos formularios para mostrarlos en el editar perfil, 
        #osea los datos que estan en la base de datos actualmente antes de editar
        #Tambien muestra los cuadros de cada dato del formulario
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        #Con esto consigo las contraseñas que me envia el cliente
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        #Con esto condigo el usuario para cambiar su contraseña
        user = Account.objects.get(username__exact=request.user.username)
        #Si la nueva contraseña es igual a confirmar contraseña
        if new_password == confirm_password:
            #Esto es un sucess de django, que verifica la validez de la contraseña
            success = user.check_password(current_password)
            #Si la contraseña cumple con los requisitos de django
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Su contraseña ha sido cambiada')
                return redirect('change_password')
            #Si la contraseña actual es erronea
            else:
                messages.error(request, 'La contraseña actual es erronea, intentelo nuevamente')
        #En caso de que no sea igual la nueva con la confirmacion
        else:
            messages.error(request, 'La contraseña no coincide con la confirmación de contraseña')
            return redirect('change_password')
    
    #Esto solo sucede si no se recibe datos en el metodo post
    return render(request, 'accounts/change_password.html')
