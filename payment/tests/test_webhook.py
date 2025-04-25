import pytest
from django.urls import reverse
from django.test import Client
from unittest.mock import patch, MagicMock
from orders.models import Order
from main.models import Product, Category
import json
from django.db import models
import stripe

@pytest.fixture
def client():
    return Client()


@pytest.fixture
def order(django_db_blocker):
    with django_db_blocker.unblock():
        category = Category.objects.create(name="Test Category", slug="test-category")
        product = Product.objects.create(name="Test Product", price=100, category=category)
        order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            address="Somewhere",
            postal_code="12345",
            city="TestCity"
        )
        order.save()
        return order


@pytest.mark.django_db
@patch("payment.views.stripe.Webhook.construct_event")
def test_stripe_webhook_success(mock_construct_event, client, order):
    # Мок події Stripe
    mock_event = MagicMock()
    mock_event.type = "checkout.session.completed"
    mock_event.data.object.client_reference_id = order.id
    mock_event.data.object.payment_intent = "pi_123456"
    mock_event.data.object.mode = "payment"
    mock_event.data.object.payment_status = "paid"
    mock_construct_event.return_value = mock_event

    payload = json.dumps({"dummy": "data"})
    sig_header = "fake_signature"

    response = client.post(
        reverse("payment:webhook"),
        data=payload,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=sig_header
    )

    assert response.status_code == 200

    order.refresh_from_db()
    assert order.paid is True



@pytest.mark.django_db
@patch("payment.views.stripe.Webhook.construct_event", side_effect=ValueError("Invalid payload"))
def test_stripe_webhook_invalid_payload(mock_construct_event, client):
    response = client.post(
        reverse("payment:webhook"),
        data=json.dumps({"dummy": "data"}),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="fake_signature"
    )
    assert response.status_code == 400


@pytest.mark.django_db
@patch("payment.views.stripe.Webhook.construct_event", side_effect=stripe.error.SignatureVerificationError("Bad sig", "body"))
def test_stripe_webhook_invalid_signature(mock_construct_event, client):
    response = client.post(
        reverse("payment:webhook"),
        data=json.dumps({"dummy": "data"}),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="invalid_signature"
    )
    assert response.status_code == 400


@pytest.mark.django_db
@patch("payment.views.stripe.Webhook.construct_event")
def test_stripe_webhook_order_not_found(mock_construct_event, client):
    # Подія з неіснуючим order.id
    mock_event = MagicMock()
    mock_event.type = "checkout.session.completed"
    mock_event.data.object.client_reference_id = 999999
    mock_event.data.object.payment_intent = "pi_fake"
    mock_event.data.object.mode = "payment"
    mock_event.data.object.payment_status = "paid"
    mock_construct_event.return_value = mock_event

    response = client.post(
        reverse("payment:webhook"),
        data=json.dumps({"dummy": "data"}),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="some_signature"
    )
    assert response.status_code == 404
