import pytest
from django.urls import reverse, resolve
from cart import views

@pytest.mark.parametrize("name,kwargs,view_func", [
    ('cart:cart_detail', {}, views.cart_detail),
    ('cart:cart_add', {'product_id': 1}, views.cart_add),
    ('cart:cart_remove', {'product_id': 1}, views.cart_remove),
    ('cart:cart_add_ajax', {'product_id': 1}, views.cart_add_ajax),
])
def test_cart_urls_reverse_and_resolve(name, kwargs, view_func):
    """
    Checks that each named route in the cart resolves correctly
    to the corresponding view function.
    """
    url = reverse(name, kwargs=kwargs)
    resolved = resolve(url)
    assert resolved.func == view_func
