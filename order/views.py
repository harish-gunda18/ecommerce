from django.shortcuts import get_object_or_404, render, HttpResponseRedirect, redirect, reverse
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order, BillingAddress
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BillingAddressForm
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt


class ItemListView(ListView):
    model = Item
    template_name = 'order/home-page.html'
    context_object_name = 'items'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'order/product-page.html'
    context_object_name = 'item'


def httpresponseredirectlogin(url):
    if 'accounts/login' in url:
        return redirect('/')
    else:
        return HttpResponseRedirect(url)


@login_required
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
    messages.success(request, 'This item has been added to your cart')
    return httpresponseredirectlogin(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user).filter(ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = OrderItem.objects.filter(order=order).filter(item=item)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            if order_item.quantity > 1:
                order_item.quantity = order_item.quantity - 1
                order_item.save()
            else:
                order_item.delete()
            messages.success(request, 'This item has been removed from your cart')
        else:
            # send message order doesn't contain item
            messages.success(request, 'Your cart does not contain this item')
    else:
        # send message order doesn't exist
        messages.success(request, 'Your cart does not contain this item')
    return httpresponseredirectlogin(request.META.get('HTTP_REFERER'))


@login_required
def order_summary(request):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        return render(request, 'order/order_summary.html', {'order': order})
    messages.success(request, 'Please add items to cart')
    return httpresponseredirectlogin(request.META.get('HTTP_REFERER'))


@login_required
def delete_from_summary(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user).filter(ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        order_item_qs = OrderItem.objects.filter(order=order).filter(item=item)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.delete()
            messages.success(request, 'This item has been removed from your cart')
        else:
            # send message order doesn't contain item
            messages.success(request, 'Your cart does not contain this item')
    else:
        # send message order doesn't exist
        messages.success(request, 'Your cart does not contain this item')
    return httpresponseredirectlogin(request.META.get('HTTP_REFERER'))


@login_required
def checkout(request):
    context = {}
    order_qs = Order.objects.filter(user=request.user).filter(ordered=False)
    order = order_qs.first()
    context['order'] = order
    saved_addresses_qs = request.user.billingaddress_set.all()
    if saved_addresses_qs.exists():
        context['saved_addresses'] = saved_addresses_qs
        default_address_qs = request.user.billingaddress_set.filter(default_address=True)
        if default_address_qs.exists():
            default_address = default_address_qs.first()
            context['default_address'] = default_address
    return render(request, 'order/checkout-page.html', context=context)


@login_required
def add_new_address(request):
    if request.method == 'POST':
        order_qs = Order.objects.filter(user=request.user).filter(ordered=False)
        order = order_qs.first()
        form = BillingAddressForm(data=request.POST)
        if form.is_valid():
            form.instance.user = request.user
            if form.cleaned_data.get('default_address'):
                billing_address_qs = request.user.billingaddress_set.filter(default_address=True)
                if billing_address_qs.exists():
                    billing_address = billing_address_qs.first()
                    billing_address.default_address = False
            form.save()
            order.billing_address = form.instance
            order.save()
            return redirect(reverse('process_payment', kwargs={'order_id': order.id}))
        else:
            print(form.errors)
    form = BillingAddressForm()
    return render(request, 'order/add-new-address.html', {'form': form})


@login_required
def select_from_saved_addresses(request):
    if request.GET.get('billing_id'):
        billing_id = request.GET.get('billing_id')
        billing_address = get_object_or_404(BillingAddress, id=int(billing_id))
        order_qs = Order.objects.filter(user=request.user).filter(ordered=False)
        order = order_qs.first()
        order.billing_address = billing_address
        order.save()
        order_id = order.id
        return redirect(reverse('process_payment', kwargs={'order_id': order_id}))
    saved_addresses_qs = request.user.billingaddress_set.all()
    return render(request, 'order/select-from-saved-addresses.html', {'saved_addresses': saved_addresses_qs})


@login_required
def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': order.get_total_price(),
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'INR',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'order/process_payment.html', {'order': order, 'form': form})


@csrf_exempt
def payment_done(request):
    return render(request, 'order/payment_done.html')


@csrf_exempt
def payment_canceled(request):
    return render(request, 'order/payment_cancelled.html')