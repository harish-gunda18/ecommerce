from django import forms
from order.models import BillingAddress


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