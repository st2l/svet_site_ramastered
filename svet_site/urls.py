from django.urls import path
from . import views

app_name = 'svet_site'

urlpatterns = [
    path('', views.index, name='index'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('lamps/', views.lamps, name='lamps'),
]