from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (('S', 'Shirt'), ('SW', 'Sports Wear'), ('OW', 'Out Wear'))
LABEL_CHOICES = (('P', 'primary'), ('S', 'secondary'), ('D', 'danger'))


class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2, default='S')
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default='P')
    slug = models.SlugField()
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('item-detail', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', kwargs={'slug': self.slug})

    def get_delete_from_summary_url(self):
        return reverse('delete-from-summary', kwargs={'slug': self.slug})


class BillingAddress(models.Model):
    address = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField(blank_label='(select country)')
    zip = models.CharField(max_length=10)
    default_address = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.OneToOneField(BillingAddress, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total_price = 0
        for order_item in self.orderitem_set.all():
            total_price += order_item.get_cost()
        return total_price

    def get_order_payment_url(self):
        return reverse('process_payment', kwargs={'order_id': self.id})


class OrderItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.item.title

    def get_cost(self):
        return self.item.price * self.quantity


class Coupon(models.Model):
    code = models.CharField(max_length=10)
    expiry_date = models.DateTimeField(blank=True, null=True)
    discount = models.IntegerField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_vendor = models.BooleanField(default=False)


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    about = models.TextField()
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    picture = models.ImageField()

    def get_absolute_url(self):
        return reverse('portfolio-detail', kwargs={'pk': self.pk})


