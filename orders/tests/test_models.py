import pytest
from orders.models import Order, OrderItem
from main.models import Product, Category

@pytest.mark.django_db
@pytest.fixture
def category():
    """Fixture to create a product category."""
    return Category.objects.create(name="Test Category", slug="test-category")

@pytest.mark.django_db
@pytest.fixture
def product(category):
    """Fixture to create a test product linked to a category."""
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        price=100,
        image="test.jpg",
        category=category
    )

@pytest.mark.django_db
@pytest.fixture
def order():
    """Fixture to create an order."""
    return Order.objects.create(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        city="Kyiv",
        address="Street 1",
        postal_code="12345"
    )

@pytest.mark.django_db
@pytest.mark.parametrize("price, quantity, expected_cost", [
    (10.00, 2, 20.00),
    (15.50, 3, 46.50),
    (25.00, 5, 125.00),
])
def test_order_item_get_cost(order, product, price, quantity, expected_cost):
    """Checks that OrderItem.get_cost() computes correctly."""
    item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
    assert item.get_cost() == expected_cost

@pytest.mark.django_db
def test_order_get_total_cost(order, product):
    """Checks total order cost calculation."""
    OrderItem.objects.create(order=order, product=product, price=10.00, quantity=2)
    OrderItem.objects.create(order=order, product=product, price=5.00, quantity=4)
    assert order.get_total_cost() == 40.00

@pytest.mark.django_db
def test_order_str(order):
    """Checks string representation of an order."""
    assert str(order) == f'Order {order.id}'

@pytest.mark.django_db
def test_order_item_str(order, product):
    """Checks string representation of an order item."""
    item = OrderItem.objects.create(order=order, product=product, price=10.00, quantity=1)
    assert str(item) == str(item.id)
