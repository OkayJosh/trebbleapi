import random
import string

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.authtoken.models import Token

from users.models import User
from users.services import UserService, AuthenticationService


class UserServiceTestCase(TestCase):

    def setUp(self):
        self.user_service = UserService()
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "account_type": "basic",
            "channel": "web",
            "fcmb_token": "abcdefg"
        }
        self.user = self.user_service.create_user(**self.user_data)

    def test_create_user(self):
        user = self.user_service.create_user(**self.user_data)
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.account_type, self.user_data["account_type"])
        self.assertEqual(user.channel, self.user_data["channel"])
        self.assertEqual(user.fcmb_token, self.user_data["fcmb_token"])
        self.assertTrue(user.check_password(self.user_data["password"]))

    def test_unique_username(self):
        user_data = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password123",
            "account_type": "basic",
            "channel": "web",
            "fcmb_token": "abcdefg"
        }
        user = self.user_service.create_user(**user_data)
        self.assertNotEqual(user.username, user_data["username"])

    def test_username_exists(self):
        self.assertTrue(self.user_service.username_exists(self.user_data["username"]))
        self.assertFalse(self.user_service.username_exists("nonexistent"))

    def test_update_user_password(self):
        new_password = "newpassword456"
        user = self.user_service.update_user_password(password=new_password, user=self.user)
        self.assertTrue(user.check_password(new_password))

    def test_update_user_fcmb_token(self):
        new_token = "new_token"
        user = self.user_service.update_user_fcmb_token(fcmb_token=new_token, user=self.user)
        self.assertEqual(user.fcmb_token, new_token)


class AuthenticationServiceTestCase(TestCase):

    def setUp(self):
        self.authentication_service = AuthenticationService()
        self.user = get_user_model().objects.create_user(
            email='test@example.com', password='password123'
        )

    def test_change_password(self):
        old_password = 'password123'
        new_password = 'newpassword456'

        token = self.authentication_service.change_password(self.user, old_password, new_password)
        self.assertIsInstance(token, Token)
        self.assertTrue(self.user.check_password(new_password))

    def test_change_password_invalid_password(self):
        old_password = 'wrongpassword'
        new_password = 'newpassword456'

        with self.assertRaises(ValueError) as context:
            self.authentication_service.change_password(self.user, old_password, new_password)
        self.assertEqual(str(context.exception), 'Invalid Password')

    def test_setup_reset_password(self):
        email = 'test@example.com'
        self.authentication_service.setup_reset_password(email)

        # check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [email])

    def test_setup_reset_password_user_not_exist(self):
        email = 'nonexistent@example.com'
        self.authentication_service.setup_reset_password(email)

        # check that no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_check_reset_token(self):
        user = self.user
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        user.reset_token = reset_token
        user.save()
        self.assertTrue(self.authentication_service.check_reset_token(reset_token))

    def test_check_reset_token_invalid_token(self):
        self.assertFalse(self.authentication_service.check_reset_token('invalidtoken'))

    def test_reset_password(self):
        user = self.user
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        user.reset_token = reset_token
        user.save()
        new_password = 'newpassword456'
        self.assertTrue(self.authentication_service.reset_password(reset_token, new_password))
        self.assertIsNone(user.reset_token)
