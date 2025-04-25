import pytest
from django.urls import reverse
from django.test import Client
from main.models import Product, Category

# Create a category for testing
@pytest.fixture
def category():
    return Category.objects.create(name="Test Category", slug="test-category")

# Create a product to use in tests
@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        category=category,
        price=100,
        discount=10
    )

# Client with session support
@pytest.fixture
def client_with_session():
    return Client()


@pytest.mark.django_db
def test_cart_add_valid(client_with_session, product):
    """
    Tests adding a product to the cart:
    - checks response status and redirect
    - verifies session cart stores correct quantity
    """
    url = reverse("cart:cart_add", args=[product.id])
    data = {
        "quantity": 2,
        "override": False
    }
    response = client_with_session.post(url, data)

    # Check redirect after adding
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_detail")

    # Check cart content in session
    session_cart = client_with_session.session.get("cart")
    assert session_cart is not None
    assert str(product.id) in session_cart
    assert session_cart[str(product.id)]["quantity"] == 2


@pytest.mark.django_db
def test_cart_remove(client_with_session, product):
    """
    Tests gradual removal of a product from the cart:
    - first removal decreases quantity
    - second completely removes the item
    """
    # Add product
    add_url = reverse("cart:cart_add", args=[product.id])
    client_with_session.post(add_url, {"quantity": 2, "override": False})

    # First removal: 1 item should remain
    remove_url = reverse("cart:cart_remove", args=[product.id])
    response = client_with_session.post(remove_url)
    assert response.status_code == 302
    assert response.url == reverse("cart:cart_detail")

    session_cart = client_with_session.session.get("cart")
    assert str(product.id) in session_cart
    assert session_cart[str(product.id)]["quantity"] == 1

    # Second removal: item should be completely removed
    response = client_with_session.post(remove_url)
    session_cart = client_with_session.session.get("cart")
    assert str(product.id) not in session_cart


@pytest.mark.django_db
def test_cart_detail_view(client_with_session, product):
    """
    Verifies that the cart detail page works correctly:
    - returns status 200
    - passes cart in context
    - uses the correct template
    """
    # Add product to cart
    add_url = reverse("cart:cart_add", args=[product.id])
    client_with_session.post(add_url, {"quantity": 1, "override": False})

    url = reverse("cart:cart_detail")
    response = client_with_session.get(url)

    assert response.status_code == 200
    assert "cart" in response.context
    assert "cart/detail.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_cart_add_ajax(client_with_session, product):
    """
    Tests AJAX addition of product to cart:
    - response returns JSON confirming success
    - contains product name and cart item count
    """
    url = reverse("cart:cart_add_ajax", args=[product.id])
    response = client_with_session.get(url)

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["product"] == product.name
    assert data["cart_count"] == 1
