from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

UserModel = get_user_model()


class AuthenticationBackendTestCase(TestCase):

    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='test@example.com',
            mobile_number='(202) 555-3485',
            password='password',
            first_name='first',
            last_name='last',
        )

    def test_email_case_insensitive_success_case(self):
        self.assertEqual(authenticate(email='test@example.com', password='password'), self.user)
        self.assertEqual(authenticate(email='TEST@example.com', password='password'), self.user)

    def test_email_case_insensitive_matching(self):
        with self.assertRaises(ValidationError):
            UserModel.objects.create_user(email='TEST@example.com', password='password')

    def test_password_success_case(self):
        self.assertEqual(authenticate(email='test@example.com', password='password'), self.user)
        self.assertEqual(authenticate(mobile_number='(202) 555-3485', password='password'), self.user)

    def test_password_failure_case(self):
        self.assertFalse(authenticate(email='test@example.com', password='passwrong'))
        self.assertFalse(authenticate(mobile_number='(202) 555-3485', password='passwrong'))
        self.assertFalse(authenticate(email='test@example.com'))

    def test_multiple_mobile_number_success(self):
        UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password', is_active=False)
        active = UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password')
        UserModel.objects.create_user(mobile_number='+61 1900 654 321', password='password', is_active=False)
        self.assertEqual(authenticate(mobile_number='+61 1900 654 321', password='password'), active)
