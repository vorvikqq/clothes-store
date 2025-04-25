from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart


def order_create(request):
    """
    View for creating order and redirecting to payment.
    If request method is POST then view redirects to payment, if not it returns page for creating order.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered HTML page with the list of products.
        Redirect(optional): If request method is POST then redirects to rendered page of stripe payment.
    """
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request=request)
        if form.is_valid():
            order = form.save()
            for item in cart:
                discounted_price = item['product'].sell_price()
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=discounted_price,
                                         quantity=item['quantity'])
            cart.clear()
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
            # return render(request,
            #               'order/created.html',
            #               {'order': order,
            #                'form': form})
    else:
        form = OrderCreateForm(request=request)
    return render(request,
                  'order/create.html',
                  {'cart': cart,
                   'form': form})
