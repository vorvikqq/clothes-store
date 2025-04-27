from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category
from cart.forms import CartAddProductForm


def popular_list(request):
    """
    Display a list of all available products marked as popular or generally available.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered HTML page with the list of products.
    """
    products = Product.objects.filter(is_available=True)[:3]

    return render(request, 'main/index/index.html', {'products': products})


def product_detail(request, slug):
    """
    Display the details about single product including the form to add it to the cart.

    Args:
        request (HttpRequest): The HTTP request object.
        slug : generated slug for product.

    Returns:
        HttpResponse: Rendered HTML page with product details.

    """
    product = get_object_or_404(Product,
                                slug=slug,
                                is_available=True)
    cart_product_form = CartAddProductForm
    return render(request,
                  'main/product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})


def product_list(request, category_slug=None):
    """
    Displays paginated list of all avaliable products with option of sort by category

    Args:
        request (HttpRequest): The HTTP request object.
        category_slug (str, optional): Slug of the category to filter products by.

    Returns:
        HttpResponse: Rendered HTML page with the product list.
    """
    page = request.GET.get('page', 1)

    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    paginator = Paginator(products, 4)
    current_page = paginator.page(int(page))
    return render(request, 'main/product/list.html',
                  {'category': category, 'categories': categories, 'products': current_page, 'slug_url': category_slug})

