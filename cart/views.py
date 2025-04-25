from django.shortcuts import render, redirect, \
    get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart or update its quantity.

    This view handles POST requests only.
    If form is valid, it adds the product to the cart.

    Args:
        request (HttpRequest): The HTTP request containing form data.
        product_id (int): ID of the product to add.

    Returns:
        HttpResponseRedirect: Redirects to the cart detail page.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the cart.

    This view handles POST requests only. It removes the specified
    product from the user's cart.

    Args:
        request (HttpRequest): The HTTP request.
        product_id (int): ID of the product to remove.

    Returns:
        HttpResponseRedirect: Redirects to the cart detail page.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    """
    Display the cart detail page.

    This view renders a template with the current contents of the cart.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered cart detail page.
    """
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})



@require_GET
def cart_add_ajax(request, product_id):
    """
    Add a product to the cart using an AJAX GET request.

    This view adds the specified product to the cart with a default quantity of 1
    and returns a JSON response.

    Args:
        request (HttpRequest): The HTTP GET request.
        product_id (int): ID of the product to add.

    Returns:
        JsonResponse: JSON response indicating success and updated cart count.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product=product, quantity=1)
    return JsonResponse({
        'success': True,
        'product': product.name,
        'cart_count': len(cart)  # повертаємо нову кількість
    })
