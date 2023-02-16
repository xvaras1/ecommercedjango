"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings

""" al final va el nombre de la app.urls """
urlpatterns = [
    #Esta es la pagina de admin, la modificaré para evitar intentos de hackeos, mientras más compleja mejor 
    path('securelogin/', admin.site.urls),
    #Falso admin, del pip instalado honeypot, la version de 2021 para evitar errores de migrate
    # con el pip instale está version django-admin-honeypot-updated-2021
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('', views.home, name="home"),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


""" '' pagina de inicio home"""