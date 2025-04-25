import pytest
from django.urls import reverse
from django.test import Client
from orders.forms import OrderCreateForm
from orders.models import Order


@pytest.mark.django_db
def test_order_create_form_valid_data():
    """Tests OrderCreateForm with valid data."""
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': 'Street 1',
        'postal_code': '12345',
        'city': 'Kyiv'
    }
    
    form = OrderCreateForm(data=data)
    assert form.is_valid()  


@pytest.mark.django_db
def test_order_create_form_invalid_data():
    """Tests OrderCreateForm with invalid data (missing first name)."""
    data = {
        'first_name': '',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': 'Street 1',
        'postal_code': '12345',
        'city': 'Kyiv'
    }
    
    form = OrderCreateForm(data=data)
    assert not form.is_valid() 


@pytest.mark.django_db
def test_order_create_form_save():
    """Tests saving an OrderCreateForm."""
    data = {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'email': 'jane@example.com',
        'address': 'Street 2',
        'postal_code': '54321',
        'city': 'Lviv'
    }
    
    form = OrderCreateForm(data=data)
    assert form.is_valid()  
    
    order = form.save(commit=False)
    assert order.first_name == 'Jane'  
    assert order.last_name == 'Doe'  


@pytest.mark.django_db
def test_order_create_form_with_request():
    """Tests OrderCreateForm with a request passed in kwargs."""
    request = None  
    data = {
        'first_name': 'Alice',
        'last_name': 'Smith',
        'email': 'alice@example.com',
        'address': 'Street 3',
        'postal_code': '67890',
        'city': 'Odessa'
    }

    form = OrderCreateForm(data=data, request=request)
    assert form.is_valid()  
    assert form.request == request  


@pytest.mark.django_db
def test_order_create_form_empty_fields():
    """Tests OrderCreateForm with empty fields."""
    data = {
        'first_name': '',
        'last_name': '',
        'email': '',
        'address': '',
        'postal_code': '',
        'city': ''
    }

    form = OrderCreateForm(data=data)
    assert not form.is_valid()  
    assert 'first_name' in form.errors  
    assert 'last_name' in form.errors  
    assert 'email' in form.errors  
    assert 'address' in form.errors  
    assert 'postal_code' in form.errors  
    assert 'city' in form.errors  
