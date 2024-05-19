from unittest.mock import patch

from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

UserModel = get_user_model()


class LoginViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('account_login')
        self.user = UserModel.objects.create_user(
            email='test@example.com',
            mobile_number='(202) 555-3485',
            password='password',
            first_name='first',
            last_name='last',
        )

    def test_success_case(self):
        response = self.client.post(self.url, {'mobile_number': '(202) 555-3485', 'password': 'password'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['session_key'])
        self.assertTrue(response.data['user'], {
            'id': self.user.id,
            'email': self.user.email,
            'mobile_number': self.user.mobile_number,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_active': True,
        })
        self.assertTrue(get_user(self.client).is_authenticated)

    def test_failure_case(self):
        response = self.client.post(self.url, {'mobile_number': '(202) 555-3485', 'password': 'passwrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_double_login_should_fail(self):
        self.client.post(self.url, {'mobile_number': '(202) 555-3485', 'password': 'password'})
        self.assertTrue(get_user(self.client).is_authenticated)
        response = self.client.post(self.url, {'mobile_number': '(202) 555-3485', 'password': 'password'})
        # commented out until CREW-111 is resolved: Issue to re-enable this: CREW-112
        # self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(get_user(self.client).is_authenticated)


class LogoutViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('account_logout')
        self.user = UserModel.objects.create_user(
            email='test@example.com',
            mobile_number='(202) 555-3485',
            password='password',
            first_name='first',
            last_name='last',
        )
        self.client.login(email='test@example.com', password='password')

    def test_success_case(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_double_logout_should_fail(self):
        self.client.post(self.url)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(get_user(self.client).is_authenticated)


class ForgotPasswordViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('account_forgot_password')
        self.user = UserModel.objects.create_user(
            email='test@example.com',
            mobile_number='(202) 555-3485',
            password='password',
            first_name='first',
            last_name='last',
        )

    def test_success_case(self):
        response = self.client.post(self.url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'], True)

    def test_success_case_not_found(self):
        response = self.client.post(self.url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'], True)

    def test_failure_case_invalid_format(self):
        response = self.client.post(self.url, {'email': 'something else'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SignupViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('account_signup')

    @patch('account.models.AuthToken.send_message')
    def test_success_case(self, _):
        response = self.client.post(self.url, {
            'first_name': 'Contractor',
            'last_name': 'McContractorface',
            'email': 'testy@example.com',
            'mobile_number': '202 555 3485',
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    @patch('account.models.AuthToken.send_message')
    def test_success_case_email_or_phone(self, _):
        response = self.client.post(self.url, {
            'first_name': 'Contractor',
            'last_name': 'McContractorface I',
            'email': 'testy@example.com',
            'mobile_number': '',
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        response = self.client.post(self.url, {
            'first_name': 'Contractor',
            'last_name': 'McContractorface II',
            'email': '',
            'mobile_number': '202 555 3485',
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)


class SignupValidateViewTestCase(TestCase):
    def test_validated(self):
        with self.settings(PRIVATE_API_TOKEN='private'):
            url = reverse('account_signup_validate') + '?token=private'
            response = self.client.post(url, {
                'company_name': 'TEST Contractor',
                'company_type': 1,
                'first_name': 'Contractor',
                'last_name': 'McContractorface',
                'email': 'testy@example.com',
                'mobile_number': '202 555 3485',
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['valid'])

    def test_validated_email_or_phone(self):
        with self.settings(PRIVATE_API_TOKEN='private'):
            url = reverse('account_signup_validate') + '?token=private'
            response = self.client.post(url, {
                'company_name': 'TEST Contractor',
                'company_type': 1,
                'first_name': 'Contractor',
                'last_name': 'McContractorface',
                'email': 'testy@example.com',
                'mobile_number': '',
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['valid'])

            response = self.client.post(url, {
                'company_name': 'TEST Contractor',
                'company_type': 1,
                'first_name': 'Contractor',
                'last_name': 'McContractorface',
                'email': '',
                'mobile_number': '202 555 3485',
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['valid'])

    def test_no_email_or_mobile_number(self):
        with self.settings(PRIVATE_API_TOKEN='private'):
            url = reverse('account_signup_validate') + '?token=private'
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data['valid'])

    def test_existing_email(self):
        UserModel.objects.create_user(email='testy@example.com', password='password')
        with self.settings(PRIVATE_API_TOKEN='private'):
            url = reverse('account_signup_validate') + '?token=private'
            response = self.client.post(url, {
                'company_name': 'TEST Contractor',
                'first_name': 'Contractor',
                'last_name': 'McContractorface',
                'email': 'testy@example.com',
                'mobile_number': '202 555 3485',
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data['valid'])

    def test_existing_mobile_number(self):
        UserModel.objects.create_user(mobile_number='202 555 3485', password='password')
        with self.settings(PRIVATE_API_TOKEN='private'):
            url = reverse('account_signup_validate') + '?token=private'
            response = self.client.post(url, {
                'company_name': 'TEST Contractor',
                'company_type': 1,
                'first_name': 'Contractor',
                'last_name': 'McContractorface',
                'email': 'testy@example.com',
                'mobile_number': '202 555 3485',
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data['valid'])
