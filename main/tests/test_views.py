import pytest
from django.urls import reverse
from main.models import Product, Category
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

# ----- Fixtures -----

@pytest.fixture
def category():
    """
    Creates a test category to be used with products.
    """
    return Category.objects.create(name="Test Category", slug="test-category")


@pytest.fixture
def image_file():
    """
    Creates a small valid GIF image file for testing.
    """
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xff\xff\xff\x21\xf9\x04\x00\x00'
        b'\x00\x00\x00\x2c\x00\x00\x00\x00'
        b'\x01\x00\x01\x00\x00\x02\x02\x44'
        b'\x01\x00\x3b'
    )
    return SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')


@pytest.fixture
def product(category, image_file):
    """
    Creates a test product linked to the test category and image.
    """
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        category=category,
        price=100.00,
        discount=10.0,
        is_available=True,
        image=image_file
    )

# ----- View Tests -----

@pytest.mark.django_db
def test_popular_list_view(client, category, image_file):
    """
    Checks that the popular products view returns 200 OK
    and includes the expected product in the response.
    """
    Product.objects.create(
        name="Popular Product",
        slug="popular-product",
        category=category,
        price=100.00,
        discount=10.0,
        is_available=True,
        image=image_file
    )

    response = client.get(reverse('main:popular_list'))
    assert response.status_code == 200
    assert b"Popular Product" in response.content


@pytest.mark.django_db
@pytest.mark.parametrize("slug, expected_product_name", [
    ('test-product', "Test Product"),
])
def test_product_detail_view(client, product, slug, expected_product_name):
    """
    Checks that the product detail page returns 200 OK
    and includes the name of the corresponding product.
    """
    response = client.get(reverse('main:product-detail', args=[slug]))
    assert response.status_code == 200
    assert expected_product_name.encode() in response.content


@pytest.mark.django_db
@pytest.mark.parametrize("category_slug, expected_product_name", [
    ('test-category', "Test Product"),
])
def test_product_list_view_with_category(client, product, category, category_slug, expected_product_name):
    """
    Checks that the product list by category returns 200 OK
    and includes the expected product.
    """
    response = client.get(reverse('main:filter-by-category', args=[category_slug]))
    assert response.status_code == 200
    assert expected_product_name.encode() in response.content


@pytest.mark.django_db
def test_product_list_view_without_category(client, product):
    """
    Checks that the general product list view returns 200 OK
    and passes the product list in the template context.
    """
    response = client.get(reverse('main:product-list'))
    assert response.status_code == 200
    assert 'products' in response.context
