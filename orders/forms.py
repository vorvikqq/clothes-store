from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    A form for creating a new order instance.

    This form is based on the Order model and includes fields for
    customer details such as name, email, and shipping address.
    """
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email',
                  'address', 'postal_code', 'city']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        order = super().save(commit=False)

        if commit:
            order.save()
        return order
