from django import forms
from .models import Account, UserProfile


#Esto es el formulario que despues invoco en el html register
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese Contraseña',
        'class': 'form-control',

    }))
    #en class le pongo form-control para que tenga el estilo css de un cuadro de texto bien hecho
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirmar Contraseña',
        'class': 'form-control',

    }))

    class Meta:
        model = Account
        #Los campos que usaré para hacer el registro del usuario
        fields = ['first_name', 'last_name', 'phone_number','email','password']

    #Con esta funcion Cambiamos class y placeholder de cada cuadro de texto en fields para que todos tengan un estilo en su cuadro de texto
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Ingrese nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Ingrese apellidos'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Ingrese su numero telefonico'
        self.fields['email'].widget.attrs['placeholder'] = 'Ingrese email'

        for field in self.fields:
            #Con esto instanciamos a cada caja de texto que hay en el campo fields arriba y llamando sus atributos, en este caso class, para eso el for
            self.fields[field].widget.attrs['class']='form-control'

    
    #Esta funcion compara las dos contraseñas ingresadas en el registro para que no sean diferentes
    def clean(self):
        #El lo que hace es tener acceso a los datos del formulario
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "El password no coincide, intentelo nuevamente"
            )
       

#Con esto creo el formulario de django de user con esos 3 datos para usarlo en views y en template después
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            #Con esto hago que cada campo de fields tendrá un class tipo form-control
            #Recuerda que el estilo del class viene del bootstrap
            self.fields[field].widget.attrs['class']='form-control'

#Con esto creo el formulario de django userprofile con esos 6 datos para usarlo en views y después en el template
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'Invalid':('Solo archivos de tipo imagen')}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
             #Con esto hago que cada campo de fields tendrá un class tipo form-control
            #Recuerda que el estilo del class viene del bootstrap
            self.fields[field].widget.attrs['class']='form-control'


        