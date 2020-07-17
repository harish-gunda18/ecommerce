from django import template
from order.models import Order

register = template.Library()


@register.filter
def cart_items_number(user):
    order_qs = Order.objects.filter(user=user, ordered=False)
    if order_qs.exists():
        return order_qs.first().orderitem_set.all().count()
    return 0