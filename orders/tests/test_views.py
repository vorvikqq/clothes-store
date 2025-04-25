import pytest
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from orders.models import Order, OrderItem
from orders.forms import OrderCreateForm
from main.models import Product, Category
from cart.cart import Cart


@pytest.fixture
def category():
    return Category.objects.create(name="Test Category", slug="test-category")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        category=category,
        price=100.00,
        discount=10.0
    )


@pytest.fixture
def cart_with_item(client, product):
    """Initializes session with one product in the cart."""
    session = client.session
    cart = session.get('cart', {})
    cart[str(product.id)] = {'quantity': 2, 'price': str(product.price)}
    session['cart'] = cart
    session.save()
    return client


@pytest.fixture
def request_factory_with_session():
    factory = RequestFactory()
    request = factory.post(reverse('orders:order_create'))
    middleware = SessionMiddleware(get_response=lambda r: r)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.mark.django_db
def test_order_create_get_view(client):
    """Tests GET request to order creation view."""
    response = client.get(reverse('orders:order_create'))
    assert response.status_code == 200
    assert 'form' in response.context
    assert 'cart' in response.context
    assert 'order/create.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_order_create_post_valid(cart_with_item, product):
    """Tests successful order creation via POST."""
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'address': '123 Main St',
        'postal_code': '12345',
        'city': 'Testville'
    }
    response = cart_with_item.post(reverse('orders:order_create'), data=data)

    assert response.status_code == 302
    assert response.url == reverse('payment:process')

    order = Order.objects.first()
    assert order.first_name == 'John'

    session = cart_with_item.session
    assert 'cart' not in session


@pytest.mark.django_db
@pytest.mark.parametrize("invalid_data", [
    {},  # All fields empty
    {'first_name': 'Only Name'},  # Insufficient data
])
def test_order_create_invalid_form(cart_with_item, invalid_data):
    """Tests order form with invalid input data."""
    response = cart_with_item.post(reverse('orders:order_create'), data=invalid_data)
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors
    assert Order.objects.count() == 0
