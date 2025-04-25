import pytest
from django.urls import reverse
from django.test import Client
from unittest.mock import patch, MagicMock
from orders.models import Order, OrderItem
from decimal import Decimal
from main.models import Product, Category

#FIXTURES
@pytest.fixture
def product(django_db_blocker):
    with django_db_blocker.unblock():
        category = Category.objects.create(name="Test Category", slug="test-category")
        return Product.objects.create(
            name="Test Product",
            price=100,
            category=category  
        )


@pytest.fixture
def order_with_items(product, django_db_blocker):
    with django_db_blocker.unblock():
        order = Order.objects.create(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='Test address',
            postal_code='12345',
            city='Test city'
        )
        OrderItem.objects.create(order=order, product=product, price=product.price, quantity=2)
        return order


@pytest.fixture
def client_with_session(order_with_items):
    client = Client()
    session = client.session
    session['order_id'] = order_with_items.id
    session.save()
    return client


#TESTS 

@patch('payment.views.stripe.checkout.Session.create')
@pytest.mark.django_db
def test_payment_process_redirect(mock_stripe_create, client_with_session):

    mock_session = MagicMock()
    mock_session.url = 'https://fake-stripe-session.com'
    mock_stripe_create.return_value = mock_session

    url = reverse('payment:process')
    response = client_with_session.get(url)

    # Перевіряємо, що статус редіректу в межах допустимих (302 або 303)
    assert response.status_code in [302, 303], f"Unexpected redirect code: {response.status_code}"
    assert response.url == 'https://fake-stripe-session.com'
    mock_stripe_create.assert_called_once()


@pytest.mark.django_db
@pytest.mark.parametrize("url_name,template", [
    ('payment:completed', 'payment/completed.html'),
    ('payment:canceled', 'payment/canceled.html'),
])
def test_payment_static_views_render(url_name, template):
    client = Client()
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == 200
    assert template in [t.name for t in response.templates]
