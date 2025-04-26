import pytest
from django.urls import reverse
from main.models import Product, Category
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest import mock

# ----- Mocking -----
mock.patch('cloudinary.uploader.upload', return_value={
    "public_id": "test_id",
    "url": "http://example.com/fake.jpg",
    "secure_url": "https://example.com/fake.jpg",
    "version": "1234567890",
    "type": "upload",
    "resource_type": "image",
    "signature": "fake_signature",
    "format": "jpg",
    "created_at": "2020-01-01T00:00:00Z",
    "bytes": 12345,
    "etag": "fake_etag",
    "placeholder": False,
}).start()

mock.patch('cloudinary.uploader.destroy', return_value={"result": "ok"}).start()

mock.patch('cloudinary.CloudinaryImage', autospec=True).start()
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
    Returns a simple image as a SimpleUploadedFile object.
    """
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=b'\x47\x49\x46\x38\x89\x61',  # minimal content for a GIF file
        content_type='image/jpeg'
    )


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
