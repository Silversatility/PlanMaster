import random
from datetime import timedelta
from string import ascii_letters, digits

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..models import AuthToken

UserModel = get_user_model()


class UserModelTestCase(TestCase):

    def test_create_stores_data(self):
        user = UserModel.objects.create_user(
            email='test@example.com',
            mobile_number='(202) 555-3485',
            password='password',
            first_name='first',
            last_name='last',
        )
        user.refresh_from_db()
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password'))
        self.assertEqual(user.first_name, 'first')
        self.assertEqual(user.last_name, 'last')
        self.assertEqual(user.mobile_number_display, '(202) 555-3485')

        with self.assertRaises(AttributeError):
            user.username

    def test_email_or_mobile_number_required(self):
        self.assertTrue(UserModel.objects.create_user(email='test2@example.com', password='password'))
        self.assertTrue(UserModel.objects.create_user(mobile_number='(202) 555-0107', password='password'))
        with self.assertRaises(ValidationError):
            UserModel.objects.create_user(password='password')

    def test_email_uniqueness(self):
        UserModel.objects.create_user(email='test@example.com', password='password')
        with self.assertRaises(ValidationError):
            UserModel.objects.create_user(email='test@example.com', password='password')

    def test_email_uniqueness_accepts_suffixes(self):
        UserModel.objects.create_user(email='test@example.com', password='password')
        user = UserModel.objects.create_user(email='test+1@example.com', password='password')
        self.assertEqual(user.email, 'test+1@example.com')

    def test_mobile_number_non_uniqueness(self):
        before = UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password', is_active=False)
        active = UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password')
        after = UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password', is_active=False)
        self.assertNotEqual(active.id, before.id)
        self.assertNotEqual(active.id, after.id)

    def test_active_mobile_number_uniqueneess_and_matching(self):
        UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password')
        with self.assertRaises(ValidationError):
            UserModel.objects.create_user(mobile_number='+61-1900-654-321', password='password')
        with self.assertRaises(ValidationError):
            UserModel.objects.create_user(mobile_number='+611900654321', password='password')

    def test_accepts_US_numbers(self):
        user = UserModel.objects.create_user(mobile_number='(202) 555-3485', password='password')
        self.assertEquals(user.mobile_number_display, '(202) 555-3485')
        self.assertEquals(user.mobile_number.as_e164, '+12025553485')

    def test_accepts_international_numbers(self):
        # International format
        user = UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password')
        self.assertEquals(user.mobile_number_display, '+61 1900 654 321')
        # E.164 format
        user = UserModel.objects.create_user(mobile_number='+611800160401', password='password')
        self.assertEquals(user.mobile_number_display, '+61 1800 160 401')

    def test_rejects_malformed_numbers(self):
        with self.assertRaises(ValidationError):
            UserModel.objects.create_user(mobile_number='', password='password')


class AuthTokenModelTestCase(TestCase):

    def test_create_stores_all_data(self):
        user = UserModel.objects.create_user(email='test@example.com', password='password')
        token = ''.join(random.choices(ascii_letters + digits, k=1024))
        now = timezone.now()
        auth_token = AuthToken.objects.create(
            user=user,
            token=token,
            timestamp_created=now,
            timestamp_expires=now + timedelta(days=30),
            authz_type=AuthToken.AUTHZ_LOGIN,
        )

        self.assertEqual(auth_token.user, user)
        self.assertEqual(auth_token.token, token)
        self.assertEqual(auth_token.timestamp_created, now)
        self.assertEqual(auth_token.timestamp_expires, now + timedelta(days=30))
        self.assertEqual(auth_token.authz_type, AuthToken.AUTHZ_LOGIN)

    def test_required_fields(self):
        user = UserModel.objects.create_user(email='test@example.com', password='password')
        token = ''.join(random.choices(ascii_letters + digits, k=1024))
        now = timezone.now()
        later = now + timedelta(days=30)
        type = AuthToken.AUTHZ_LOGIN

        with self.assertRaises(ValidationError):
            AuthToken.objects.create(token=token, timestamp_created=now, timestamp_expires=later, authz_type=type)
        with self.assertRaises(ValidationError):
            AuthToken.objects.create(user=user, timestamp_created=now, timestamp_expires=later, authz_type=type)
        with self.assertRaises(ValidationError):
            AuthToken.objects.create(user=user, token=token, timestamp_expires=later, authz_type=type)
        with self.assertRaises(ValidationError):
            AuthToken.objects.create(user=user, token=token, timestamp_created=now, authz_type=type)
        with self.assertRaises(ValidationError):
            AuthToken.objects.create(user=user, token=token, timestamp_created=now, timestamp_expires=later)
