import pytest
from django.urls import reverse
from django.test import Client


@pytest.mark.django_db
def test_order_create_url():
    """Tests if the order creation URL is accessible."""
    url = reverse('orders:order_create')
    response = Client().get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_create_view():
    """Tests if the order creation view returns context with form."""
    url = reverse('orders:order_create')
    response = Client().get(url)
    assert 'form' in response.context
    assert response.status_code == 200
