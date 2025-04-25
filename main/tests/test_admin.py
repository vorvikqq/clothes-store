import pytest
from django.contrib import admin
from main.admin import CategoryAdmin, ProductAdmin
from main.models import Category, Product

@pytest.mark.django_db
def test_category_registered():
    """
    Verifies that the Category model is registered in the admin panel
    and uses the correct admin class (CategoryAdmin).
    """
    assert Category in admin.site._registry
    assert isinstance(admin.site._registry[Category], CategoryAdmin)

@pytest.mark.django_db
def test_product_registered():
    """
    Verifies that the Product model is registered in the admin panel
    and uses the correct admin class (ProductAdmin).
    """
    assert Product in admin.site._registry
    assert isinstance(admin.site._registry[Product], ProductAdmin)

@pytest.mark.parametrize("admin_class, expected", [
    (CategoryAdmin, {
        "list_display": ('id', 'name', 'is_visible', 'sort'),
        "list_display_links": ('name', 'id'),
        "list_editable": ('is_visible', 'sort'),
        "prepopulated_fields": {'slug': ('name',)},
    }),
    (ProductAdmin, {
        "list_display": ('id', 'name', 'price', 'discount', 'is_available', 'sort', 'created_at', 'updated_at'),
        "list_display_links": ('name', 'id'),
        "list_editable": ('is_available', 'sort', 'price', 'discount'),
        "prepopulated_fields": {'slug': ('name',)},
        "list_filter": ['is_available', 'created_at', 'updated_at'],
    }),
])
def test_admin_config(admin_class, expected):
    """
    Verifies that admin classes have the correct configuration:
    - list_display
    - list_display_links
    - list_editable
    - prepopulated_fields
    - list_filter (if defined)
    """
    for attr, value in expected.items():
        assert getattr(admin_class, attr) == value
