import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_payment_completed_url():
    client = Client()
    url = reverse('payment:completed')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_payment_canceled_url():
    client = Client()
    url = reverse('payment:canceled')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_payment_webhook_url_post():
    client = Client()
    url = reverse('payment:webhook')

    headers = {
        'HTTP_STRIPE_SIGNATURE': 'test_signature'
    }

    response = client.post(url, data='{}', content_type='application/json', **headers)
    assert response.status_code in [200, 400]
