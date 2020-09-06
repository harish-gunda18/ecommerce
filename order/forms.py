from django import forms
from order.models import BillingAddress, Coupon, Portfolio
from phonenumber_field.formfields import PhoneNumberField


class BillingAddressForm(forms.ModelForm):

    class Meta:
        model = BillingAddress
        fields = ('address', 'address2', 'country', 'zip', 'default_address')
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': '1234 Main St'}),
            'address2': forms.TextInput(attrs={'placeholder': 'Apartment or suite'}),
        }
        labels = {
            'address2': 'address2(optional)',
            'default_address': 'Make this your default address'
        }


class PortfolioForm(forms.ModelForm):

    class Meta:
        model = Portfolio
        fields = ('about', 'email', 'phone_number', 'picture')


class CouponForm(forms.Form):

    class Meta:
        fields = ('code',)
        labels = {
            'code': 'coupon code',
        }
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': "Promo code"})
        }


class ContactForm(forms.Form):
    First_Name = forms.CharField()
    Last_Name = forms.CharField()
    Email = forms.EmailField()
    Phone_Number = PhoneNumberField()
