import pytest
from django.urls import reverse, resolve
from main.views import popular_list, product_list, product_detail

@pytest.mark.parametrize("url_name, expected_view", [
    ('main:popular_list', popular_list),
    ('main:product-list', product_list),
    ('main:product-detail', product_detail),
    ('main:filter-by-category', product_list),
])
def test_urls_resolve_to_correct_view(url_name, expected_view):
    """
    Ensures named URLs resolve to the correct view functions.
    """
    args = ['test-category'] if 'filter-by-category' in url_name else ['test-product'] if 'detail' in url_name else []
    url = reverse(url_name, args=args)
    resolved = resolve(url)
    assert resolved.func == expected_view
