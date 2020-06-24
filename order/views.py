from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order
from django.utils import timezone


class ItemListView(ListView):
    model = Item
    template_name = 'order/home-page.html'
    context_object_name = 'items'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'order/product-page.html'
    context_object_name = 'item'


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user).filter(ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = OrderItem.objects.filter(order=order).filter(item=item)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
        else:
            OrderItem.objects.create(item=item, order=order)
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        OrderItem.objects.create(item=item, order=order)
    return redirect('item-detail', slug=slug)


