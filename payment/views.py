from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from decimal import Decimal
from orders.models import Order
from django.conf import settings

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    """
    Handle the Stripe payment session creation and redirect user to Stripe Checkout.

    This view is triggered when the user proceeds to payment. It retrieves the current order
    from the session, creates a Stripe Checkout session with the order's line items, and
    redirects the user to the Stripe-hosted payment page.

    GET request only because of the redirection from order_create.

    Args:
        request (HttpRequest): The HTTP request containing session data.

    Returns:
        HttpResponseRedirect: Redirects to the Stripe Checkout page.
    """
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'GET':
        success_url = request.build_absolute_uri(
            reverse('payment:completed')
        )
        cancel_url = request.build_absolute_uri(
            reverse('payment:canceled')
        )
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        for item in order.items.all():
            price = item.product.sell_price()
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(price * Decimal(100)),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    }
                },
                'quantity': item.quantity
            })
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)


def payment_completed(request):
    """
    Display the payment completed page.

    This view is shown to the user after a successful Stripe payment.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered template for payment success.
    """
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    """
    Display the payment canceled page.

    This view is shown to the user if he goes back from and canceles Stripe payment.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered template for payment cancel.
    """
    return render(request, 'payment/canceled.html')