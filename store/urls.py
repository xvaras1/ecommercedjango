from django.urls import path
from . import views

#Aqui llamo las funciones de views.py
#Aqui están las url store/category/producto
urlpatterns = [
    path('', views.store, name="store"),
    path('<slug:category_slug>/', views.store, name='products_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]   