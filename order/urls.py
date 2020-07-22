from django.urls import path, include
from .views import ItemListView, ItemDetailView, add_to_cart, remove_from_cart, order_summary, delete_from_summary, \
    checkout, add_new_address, select_from_saved_addresses, payment_process, payment_done, payment_canceled

urlpatterns = [
    path('', ItemListView.as_view(), name='item-list'),
    path('product/<slug:slug>', ItemDetailView.as_view(), name='item-detail'),
    path('add-to-cart/<slug:slug>', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug:slug>', remove_from_cart, name='remove-from-cart'),
    path('delete-from-summary/<slug:slug>', delete_from_summary, name='delete-from-summary'),
    path('order-summary', order_summary, name='order-summary'),
    path('check-out', checkout, name='check-out'),
    path('add-new-address', add_new_address, name='add-new-address'),
    path('select-from-saved-addresses/', select_from_saved_addresses, name='select-from-saved-addresses'),
    path('process-payment/<int:order_id>', payment_process, name='process_payment'),
    path('payment-done/', payment_done, name='payment_done'),
    path('payment-cancelled/', payment_canceled, name='payment_cancelled'),
]
