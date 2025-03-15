from django.urls import path
from . import views

app_name = 'svet_site'  # Add this line to register the namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
]