import stripe
import stripe.error
from django.conf import settings
from django.http import HttpResponse
from main.models import Product
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events, specifically the 'checkout.session.completed' event.

    This view listens for POST requests sent by Stripe when a payment session is completed.
    If the event is valid and the session is marked as 'paid', it updates the corresponding order
    in the database, marking it as paid and saving the Stripe payment intent ID.

    Steps:
    1. Verify the Stripe signature to ensure request authenticity.
    2. Check if the event type is 'checkout.session.completed'.
    3. Retrieve the related order by client_reference_id.
    4. If the order exists and session is valid, mark the order as paid.

    Returns:
        HttpResponse: 200 on success, 400/404 on error.
    """
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )

    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)


    if event.type == 'checkout.session.completed':
        session = event.data.object

        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            order.paid = True
            order.stripe_id = session.payment_intent
            order.save()

    return HttpResponse(status=200)