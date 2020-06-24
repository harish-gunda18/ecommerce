from django.urls import path, include
from .views import ItemListView, ItemDetailView, add_to_cart

urlpatterns = [
    path('', ItemListView.as_view(), name='item-list'),
    path('product/<slug:slug>', ItemDetailView.as_view(), name='item-detail'),
    path('add-to-cart/<slug:slug>', add_to_cart, name='add-to-cart'),
]
