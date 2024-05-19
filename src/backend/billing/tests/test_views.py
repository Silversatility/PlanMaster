import base64
import json
import os

import stripe

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from unittest import mock
from unittest.mock import MagicMock

from account.models import User


class StripeCustomerCreateViewTestCase(TestCase):
    @mock.patch.object(stripe.Customer, 'create')
    def test_post(self, mocked_customer):
        mock_object = MagicMock()
        mock_object.configure_mock(id='cus_P9dn2Jnfd')
        mocked_customer.return_value = mock_object

        user = User.objects.create(email='test@test.com', password='123')
        url = reverse('stripe_customer_create')
        data = {
            'user': user.id,
            'source': 'src_jS2fOe23pdnJfdDF'
        }
        self.client.force_login(user)
        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(pk=user.pk).stripe_customer)


class SubscribeCustomerViewTestCase(TestCase):
    @mock.patch.object(stripe.Subscription, 'create')
    def test_post(self, mocked_subscription):
        mock_object = MagicMock()
        mock_object.configure_mock(id='sub_f90SdwWDs2FOpIid')
        mocked_subscription.return_value = mock_object

        user = User.objects.create(email='test@test.com', password='123', stripe_customer='cus_P9dn2Jnfd')
        url = reverse('subscribe_customer')
        data = {
            'user': user.id,
            'plan': 'builder_annual'
        }
        self.client.force_login(user)
        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(pk=user.pk).stripe_subscription)
        self.assertFalse(User.objects.get(pk=user.pk).has_active_subscription)


class CancelSubscriptionViewTestCase(TestCase):
    @mock.patch.object(stripe.Subscription, 'retrieve')
    def test_post(self, mocked_subscription):
        user = User.objects.create(
            email='test@test.com',
            password='123',
            stripe_customer='cus_P9dn2Jnfd',
            stripe_subscription='sub_f90SdwWDs2FOpIid'
        )
        url = reverse('cancel_subscription')
        data = {
            'user': user.id,
        }
        self.client.force_login(user)
        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.get(pk=user.pk).stripe_subscription)


class FailedChargeViewTestCase(TestCase):
    @mock.patch.object(stripe.Webhook, 'construct_event')
    def test_post(self, mocked_webhook):
        user = User(
            email='test@test.com',
            stripe_customer='cus_P9dn2Jnfd',
            stripe_subscription='sub_f90SdwWDs2FOpIid',
            has_active_subscription=True
        )
        user.set_password('123')
        user.save()
        file_path = os.path.dirname(__file__) + '/data/stripe_failed_charge_webhook.json'

        with open(file_path) as f:
            data = json.load(f)

        data['data']['object']['customer'] = user.stripe_customer
        url = reverse('charge_failed')
        auth_headers = {'HTTP_STRIPE_SIGNATURE': 'test_signature'}
        response = self.client.post(url, data=json.dumps(data), content_type="application/json", **auth_headers)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.has_active_subscription)
        self.assertFalse(User.objects.get(id=user.id).has_active_subscription)


class ChargeSucceededViewTestCase(TestCase):
    @mock.patch.object(stripe.Subscription, 'retrieve')
    @mock.patch.object(stripe.Webhook, 'construct_event')
    def test_post(self, mocked_webhook, mocked_subscription):
        mock_object = MagicMock()
        mock_object.configure_mock(id='sub_f90SdwWDs2FOpIid')
        mocked_subscription.return_value = mock_object

        user = User(
            email='test@test.com',
            stripe_customer='cus_P9dn2Jnfd',
            stripe_subscription='sub_f90SdwWDs2FOpIid'
        )
        user.set_password('123')
        user.save()
        file_path = os.path.dirname(__file__) + '/data/stripe_succeeded_charge_webhook.json'

        with open(file_path) as f:
            data = json.load(f)

        data['data']['object']['customer'] = user.stripe_customer
        url = reverse('charge_succeeded')
        auth_headers = {'HTTP_STRIPE_SIGNATURE': 'test_signature'}
        response = self.client.post(url, data=json.dumps(data), content_type="application/json", **auth_headers)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.stripe_subscription)
        self.assertFalse(user.has_active_subscription)
        self.assertTrue(User.objects.get(id=user.id).has_active_subscription)


class ApplyPromoCodeViewTestCase(TestCase):
    @mock.patch.object(stripe.Subscription, 'retrieve')
    def test_post(self, mocked_subscription):
        user = User.objects.create(email='test@test.com', password='123', stripe_subscription='sub_f90SdwWDs2FOpIid')
        url = reverse('apply_promo_code')
        data = {
            'user': user.id,
            'code': '25OFF'
        }
        self.client.force_login(user)
        response = self.client.post(url, data=data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
