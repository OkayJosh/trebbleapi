import json
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import RequestFactory, TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from users.models import User, SystemContact, FAQ, Blog, Testimonials, SystemPlanDiscount, Benefits, Plan
from users.models import ContactUs
from users.views import ContactUsViewSet, SystemContactViewSet, FacebookLoginView, LoginView, \
    FAQViewSet, FullBlogViewSet, SystemPlanDiscountViewSet


class ContactUsViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ContactUsViewSet.as_view(actions={'post': 'create'})
        self.user = User.objects.create(
            email='test@example.com',
            password='password123'
        )
        self.data = {
            'name': 'test',
            'email': 'test@example.com',
            'message': 'test message'
        }

    def test_create_contact_us(self):
        request = self.factory.post('/contact-us/', data=self.data)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactUs.objects.count(), 1)
        self.assertEqual(ContactUs.objects.get().name, 'test')

    def test_create_contact_us_not_authenticated(self):
        request = self.factory.post('/contact-us/', data=self.data)
        response = self.view(request)
        self.assertEqual(response.status_code, 201)

    def test_create_contact_us_not_admin(self):
        request = self.factory.post('/contact-us/', data=self.data)
        request.user = User.objects.create_user(
            email='test2@example.com',
            password='password123'
        )
        response = self.view(request)
        self.assertEqual(response.status_code, 201)

    def test_pagination(self):
        for i in range(11):
            ContactUs.objects.create(name=f'test{i}', email=f'test{i}@example.com', message='test message')
        request = self.factory.get('/contact-us/')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 9)
        self.assertEqual(response.data['next'], 'http://testserver/contact-us/?page=2&page_size=9')
        self.assertIsNone(response.data['previous'])
        request = self.factory.get('/contact-us/?page=2')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNone(response.data['next'])
        self.assertEqual(response.data['previous'], 'http://testserver/contact-us/?page=1&page_size=9')

    def test_create_contact_us_throttle_authenticated(self):
        request = self.factory.post('/contact-us/', data=self.data)
        request.user = self.user
        response = None
        for i in range(11):
            response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactUs.objects.count(), 11)

    def test_create_contact_us_throttle_not_authenticated(self):
        request = self.factory.post('/contact-us/', data=self.data)
        response = None
        for i in range(11):
            response = self.view(request)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(ContactUs.objects.count(), 10)


class SystemContactViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = SystemContactViewSet.as_view(actions={'post': 'create'})
        self.user = User.objects.create(
            email='test@example.com',
            password='password123'
        )
        self.data = {
            'email': 'test@example.com',
            'phone_number': '123-456-7890',
            'address': '123 Example St.'
        }

    def test_create_system_contact(self):
        request = self.factory.post('/contact-info/', data=self.data)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SystemContact.objects.count(), 1)
        self.assertEqual(SystemContact.objects.get().email, 'test@example.com')

    def test_create_system_contact_not_authenticated(self):
        request = self.factory.post('/contact-info/', data=self.data)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_create_system_contact_not_admin(self):
        request = self.factory.post('/contact-info/', data=self.data)
        request.user = User.objects.create_user(
            email='test2@example.com', password='password123')
        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_get_system_contact(self):
        SystemContact.objects.create(
            email='test@example.com',
            phone_number='123-456-7890',
            address='123 Example St.'
        )
        request = self.factory.get('/contact-info/')
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_system_contact_admin(self):
        SystemContact.objects.create(
            email='test@example.com',
            phone_number='123-456-7890',
            address='123 Example St.'
        )
        request = self.factory.patch('/contact-info/1/', data={'email': 'test2@example.com'})
        request.user = self.user
        response = self.view(request, pk='1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SystemContact.objects.get().email, 'test2@example.com')

    def test_update_system_contact_not_admin(self):
        SystemContact.objects.create(
            email='test@example.com',
            phone_number='123-456-7890',
            address='123 Example St.'
        )
        request = self.factory.patch('/contact-info/1/', data={'email': 'test2@example.com'})
        request.user = User.objects.create_user(
            email='test2@example.com', password='password123')
        response = self.view(request, pk='1')
        self.assertEqual(response.status_code, 403)


class FacebookLoginViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.token = Token.objects.create(user=self.user)
        self.mock_graph = MagicMock()
        self.mock_graph.get_object.return_value = {'email': 'test@example.com'}
        # replace the GraphAPI class with the mock object
        FacebookLoginView.GraphAPI = self.mock_graph

    def test_facebook_login_valid_token(self):
        data = {'access_token': 'valid_token'}
        response = self.client.post('/facebook-login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token'], self.token.key)
        self.assertEqual(response.data['user_id'], self.user.pk)
        self.assertEqual(response.data['email'], self.user.email)
        self.mock_graph.get_object.assert_called_once()

    @patch('FacebookLoginView.GraphAPI', side_effect=Exception)
    def test_facebook_login_invalid_token(self):
        data = {'access_token': 'invalid_token'}
        response = self.client.post('/facebook-login/', data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid token.')

    def test_facebook_login_no_token(self):
        response = self.client.post('/facebook-login/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'access_token is required.')

class GoogleLoginViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.token = Token.objects.create(user=self.user)

    @patch('GoogleLoginView.build')
    def test_google_login_valid_token(self, mock_build):
        # create a mock service object
        mock_service = MagicMock()
        # set the return value of the userinfo().get().execute() method
        mock_service.userinfo.return_value.get.return_value.execute.return_value = {'email': 'test@example.com'}
        # set the return value of the build method
        mock_build.return_value = mock_service

        data = {'id_token': 'valid_token'}
        response = self.client.post('/google-login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token'], self.token.key)
        self.assertEqual(response.data['user_id'], self.user.pk)
        self.assertEqual(response.data['email'], self.user.email)
        # assert that the build and userinfo methods were called
        mock_build.assert_called_once()
        mock_service.userinfo.return_value.get.return_value.execute.assert_called_once()

    @patch('GoogleLoginView.build', side_effect=Exception)
    def test_google_login_invalid_token(self, mock_build):
        data = {'id_token': 'invalid_token'}
        response = self.client.post('/google-login/', data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid token.')

    def test_google_login_missing_token(self):
        response = self.client.post('/google-login/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'id_token is required.')


class LoginViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password'
        )

    def test_login_valid_request(self):
        # Send a valid login request
        data = {
            "email": "user@example.com",
            "password": "password",
            "remember_me": True,
            "device_name":"Windows",
            "device_id":"12345"
        }
        headers = {
            "Device-Name": "Windows",
            "Device-Id":"12345"
        }
        response = self.client.post(
            '/login/', data=data, headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_id'], self.user.pk)

    def test_login_invalid_request(self):
        # Send an invalid login request
        data = {
            "email": "user@example.com",
            "password": "wrong_password",
            "remember_me": True,
            "device_name": "Windows",
            "device_id": "12345"
        }
        headers = {
            "Device-Name": "Windows",
            "Device-Id":"12345"
        }
        response = self.client.post(
            '/login/', data=data, headers=headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_view_max_devices(self):
        # Create a user
        user = User.objects.create_user(email='user@example.com', password='password')
        # Log the user in from 2 devices
        user.logged_devices.create(device_name='Windows', device_id='12345')
        user.logged_devices.create(device_name='Mac', device_id='67890')

        # Attempt to log in from a third device
        headers = {
            "Device-Name": "Linux",
            "Device-Id": "abcde"
        }
        data = {
            "email": "user@example.com",
            "password": "password",
            "remember_me": True,
            "device_name": "Linux",
            "device_id": "abcde"
        }
        response = self.client.post(reverse('login'), data=data, headers=headers)

        # Assert that the login request returns a 400 bad request error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            "error": "You have already logged in from 2 devices. Logout from one of the devices to continue"})

    def test_token_expiration_time(self):
        # Test token expiration time when remember_me is True
        data = {
            'email': 'user@example.com',
            'password': 'password',
            'remember_me': True
        }
        request = self.factory.post('/login/', data)
        view = LoginView.as_view()
        response = view(request)
        token = response.data['token']
        self.assertTrue(timezone.now() + timedelta(days=14) - token.expires <= timedelta(seconds=1))

        # Test token expiration time when remember_me is False
        data = {
            'email': 'user@example.com',
            'password': 'password',
            'remember_me': False
        }
        request = self.factory.post('/login/', data)
        view = LoginView.as_view()
        response = view(request)
        token = response.data['token']
        self.assertTrue(
            timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRY) - token.expires <= timedelta(seconds=1))


class CreateUserViewTestCase(APITestCase):

    def setUp(self):
        self.valid_payload = {
            "email": "user@example.com",
            "password": "password",
            "privacy": True
        }
        self.invalid_payload_missing_email = {
            "password": "password",
            "privacy": True
        }
        self.invalid_payload_missing_password = {
            "email": "user@example.com",
            "privacy": True
        }
        self.invalid_payload_missing_privacy = {
            "email": "user@example.com",
            "password": "password",
        }

    def test_create_user_valid_payload(self):
        response = self.client.post(reverse('signup'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.valid_payload['email'])
        self.assertNotIn('password', response.data)

    def test_create_user_invalid_payload_missing_email(self):
        response = self.client.post(reverse('signup'), data=json.dumps(self.invalid_payload_missing_email),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_create_user_invalid_payload_missing_password(self):
        response = self.client.post(reverse('signup'), data=json.dumps(self.invalid_payload_missing_password),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field is required.')

    def test_create_user_invalid_payload_missing_privacy(self):
        response = self.client.post(reverse('signup'), data=json.dumps(self.invalid_payload_missing_privacy),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['privacy'][0], 'This field is required.')


class NewsletterViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('newsletter-list')

    def test_throttling_for_unauthenticated_users(self):
        self.client.force_authenticate(user=None)
        for i in range(11):
            response = self.client.post(self.url, {'email': 'test@example.com'})
            self.assertEqual(response.status_code, 200 if i < 10 else 429)

    def test_no_throttling_for_authenticated_users(self):
        for i in range(100):
            response = self.client.post(self.url, {'email': 'test@example.com'})
            self.assertEqual(response.status_code, 201)


class FAQViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
        self.normal_user = User.objects.create_user(username='normal', password='normalpassword')
        self.faq1 = FAQ.objects.create(question='Question 1', answer='Answer 1')
        self.faq2 = FAQ.objects.create(question='Question 2', answer='Answer 2')

    def test_get_queryset(self):
        request = self.factory.get('/home-faq/')
        view = FAQViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['question'], 'Question 2')
        self.assertEqual(response.data[1]['question'], 'Question 1')

    def test_create_faq_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('home-faq-list'), {'question': 'Question 3', 'answer': 'Answer 3'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FAQ.objects.count(), 3)

    def test_create_faq_unauthenticated(self):
        response = self.client.post(reverse('home-faq-list'), {'question': 'Question 3', 'answer': 'Answer 3'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(FAQ.objects.count(), 2)

    def test_create_faq_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(reverse('home-faq-list'), {'question': 'Question 3', 'answer': 'Answer 3'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(FAQ.objects.count(), 2)


class FullBlogViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
        self.normal_user = User.objects.create_user(username='normal', password='normalpassword')
        self.blog1 = Blog.objects.create(name='Blog 1', content='Content 1', image='path/to/image1', thumbnail_image='path/to/thumbnail_image1', medium_image='path/to/medium_image1', large_image='path/to/large_image1')
        self.blog2 = Blog.objects.create(name='Blog 2', content='Content 2', image='path/to/image2', thumbnail_image='path/to/thumbnail_image2', medium_image='path/to/medium_image2', large_image='path/to/large_image2')

    def test_get_queryset(self):
        request = self.factory.get(reverse('blog-list'))
        view = FullBlogViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['slug'], 'blog-2')
        self.assertEqual(response.data[1]['slug'], 'blog-1')

    def test_create_blog_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('blog-list'), {'name': 'Blog 3', 'content': 'Content 3', 'image': 'path/to/image3', 'thumbnail_image': 'path/to/thumbnail_image3', 'medium_image': 'path/to/medium_image3', 'large_image': 'path/to/large_image3'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Blog.objects.count(), 3)
        self.assertEqual(Blog.objects.get(name='Blog 3').slug, 'blog-3')

    def test_create_blog_unauthenticated(self):
        response = self.client.post(reverse('blog-list'), {'name': 'Blog 3', 'content': 'Content 3', 'image': 'path/to/image3', 'thumbnail_image': 'path/to/thumbnail_image3', 'medium_image': 'path/to/medium_image3', 'large_image': 'path/to/large_image3'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Blog.objects.count(), 2)

    def test_update_blog_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(reverse('blog-list')+str(self.blog1.id)+'/', {'name': 'Blog 1 Updated', 'content': 'Content 1 Updated', 'image': 'path/to/image1_updated', 'thumbnail_image': 'path/to/thumbnail_image1_updated', 'medium_image': 'path/to/medium_image1_updated', 'large_image': 'path/to/large_image1_updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Blog.objects.count(), 2)
        self.assertEqual(Blog.objects.get(id=self.blog1.id).name, 'Blog 1 Updated')
        self.assertEqual(Blog.objects.get(id=self.blog1.id).slug, 'blog-1-updated')

    def test_update_blog_unauthenticated(self):
        response = self.client.put(reverse('blog-list')+str(self.blog1.id)+'/', {'name': 'Blog 1 Updated', 'content': 'Content 1 Updated', 'image': 'path/to/image1_updated', 'thumbnail_image': 'path/to/thumbnail_image1_updated', 'medium_image': 'path/to/medium_image1_updated', 'large_image': 'path/to/large_image1_updated'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Blog.objects.count(), 2)
        self.assertEqual(Blog.objects.get(id=self.blog1.id).name, 'Blog 1')

    def test_delete_blog_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('blog-list')+str(self.blog1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Blog.objects.count(), 1)

    def test_delete_blog_unauthenticated(self):
        response = self.client.delete(reverse('blog-list')+str(self.blog1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Blog.objects.count(), 2)
        self.assertEqual(Blog.objects.get(id=self.blog1.id).name, 'Blog 1')

    def test_pagination(self):
        for i in range(11):
            Blog.objects.create(name='Blog {}'.format(i), content='Content {}'.format(i), image='path/to/image{}'.format(i), thumbnail_image='path/to/thumbnail_image{}'.format(i), medium_image='path/to/medium_image{}'.format(i), large_image='path/to/large_image{}'.format(i))
        response = self.client.get(reverse('blog-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 9)
        self.assertEqual(response.data[0]['slug'], 'blog-10')
        response = self.client.get('/blog/', {'page_size': '5', 'page': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]['slug'], 'blog-10')


class TestimonialViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.testimonial1 = Testimonials.objects.create(ratings=0.3, testimonials='Testimonial 1', user=self.user1)
        self.testimonial2 = Testimonials.objects.create(ratings=.4, testimonials='Testimonial 2', user=self.user2)

    def test_create_testimonial(self):
        self.client.force_authenticate(self.user1)
        data = {'ratings': 5, 'testimonials': 'Testimonial 3'}
        response = self.client.post(reverse('testimonials-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Testimonials.objects.count(), 3)
        self.assertEqual(Testimonials.objects.get(ratings=5).testimonials, 'Testimonial 3')

    def test_create_testimonial_unauthenticated(self):
        data = {'ratings': 5, 'testimonials': 'Testimonial 3'}
        response = self.client.post(reverse('testimonials-list'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Testimonials.objects.count(), 2)

    def test_list_testimonials(self):
        response = self.client.get(reverse('testimonials-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0.2)
        self.assertEqual(response.data[0]['user']['username'], 'user2')
        self.assertEqual(response.data[0]['percentage'], 400)

    def test_retrieve_testimonial(self):
        response = self.client.get(reverse('testimonials-list')+str(self.testimonial1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'user1')
        self.assertEqual(response.data['ratings'], 0.3)
        self.assertEqual(response.data['testimonials'], 'Testimonial 1')

    def test_update_testimonial(self):
        self.client.force_authenticate(self.user1)
        data = {'ratings': 0.4, 'testimonials': 'Testimonial 1 updated'}
        response = self.client.put(reverse('testimonials-list')+str(self.testimonial1.id)+'/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'user1')
        self.assertEqual(response.data['ratings'], 0.3)
        self.assertEqual(response.data['testimonials'], 'Testimonial 1 updated')

    def test_update_testimonial_unauthenticated(self):
        data = {'ratings': 4, 'testimonials': 'Testimonial 1 updated'}
        response = self.client.put(reverse('testimonials-list')+str(self.testimonial1.id)+'/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Testimonials.objects.get(id=self.testimonial1.id).testimonials, 'Testimonial 1')
        self.assertEqual(Testimonials.objects.get(id=self.testimonial1.id).ratings, 3)

    def test_update_testimonial_forbidden(self):
        self.client.force_authenticate(self.user2)
        data = {'ratings': 4, 'testimonials': 'Testimonial 1 updated'}
        response = self.client.put(reverse('testimonials-list')+str(self.testimonial1.id)+'/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Testimonials.objects.get(id=self.testimonial1.id).testimonials, 'Testimonial 1')
        self.assertEqual(Testimonials.objects.get(id=self.testimonial1.id).ratings, 3)

    def test_delete_testimonial(self):
        self.client.force_authenticate(self.user1)
        response = self.client.delete(reverse('testimonials-list')+str(self.testimonial1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Testimonials.objects.count(), 1)

    def test_delete_testimonial_unauthenticated(self):
        response = self.client.delete(reverse('testimonials-list')+str(self.testimonial1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Testimonials.objects.count(), 2)

    def test_delete_testimonial_forbidden(self):
        self.client.force_authenticate(self.user2)
        response = self.client.delete(reverse('testimonials-list')+str(self.testimonial1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Testimonials.objects.count(), 2)


class SystemPlanDiscountViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = SystemPlanDiscountViewSet.as_view(actions={'post': 'create'})
        self.user_admin = User.objects.create_superuser(
            email='testsuper@example.com',
            password='password123'
        )
        self.user_normal = User.objects.create_superuser(
            email='test@example.com',
            password='password123'
        )
        self.data = {
            'yearly_discount': 0.25,
        }

    def test_create_system_discount_admin(self):
        request = self.factory.post(reverse('plan-discount-yearly-list'), data=self.data)
        request.user = self.user_admin
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SystemPlanDiscount.objects.count(), 1)
        self.assertEqual(SystemPlanDiscount.objects.get().yearly_discount, self.data['yearly_discount'])

    def test_create_system_discount_not_authenticated(self):
        request = self.factory.post(reverse('plan-discount-yearly-list'), data=self.data)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_create_system_discount_not_admin(self):
        request = self.factory.post(reverse('plan-discount-yearly-list'), data=self.data)
        request.user = self.user_normal
        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_get_system_discount(self):
        SystemPlanDiscount.objects.create(
            yearly_discount=0.25,
        )
        request = self.factory.get(reverse('plan-discount-yearly-list'))
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['yearly_discount'], 0.25)

    def test_update_system_contact_admin(self):
        SystemPlanDiscount.objects.create(
            yearly_discount=0.25,
        )
        data = self.data['yearly_discount'] = 0.21
        request = self.factory.patch(reverse('plan-discount-yearly-list')+'1/', data=data)
        request.user = self.user_admin
        response = self.view(request, pk='1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SystemPlanDiscount.objects.get().yearly_discount, data['yearly_discount'])

    def test_update_system_contact_not_admin(self):
        data = self.data['yearly_discount'] = 0.21
        request = self.factory.patch(reverse('plan-discount-yearly-list')+'1/', data=data)
        request.user = self.user_normal
        response = self.view(request, pk='1')
        self.assertEqual(response.status_code, 403)


class PlanViewSetTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='password')
        self.user = User.objects.create_user(username='user', password='password')
        self.benefit1 = Benefits.objects.create(details='Benefit 1')
        self.benefit2 = Benefits.objects.create(details='Benefit 2')
        self.plan1 = Plan.objects.create(name='Plan 1', monthly_price=100.0, benefits=self.benefit1)
        self.plan2 = Plan.objects.create(name='Plan 2', monthly_price=200.0, benefits=self.benefit2)

    def test_list_plans(self):
        response = self.client.get(reverse('blog-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Plan 2')
        self.assertEqual(response.data[0]['plan_benefits'][0]['details'], 'Benefit 2')
        self.assertEqual(response.data[0]['price_per_month'], 200.0)
        self.assertEqual(response.data[0]['price_per_year'], 2400.0)

    def test_create_plan(self):
        self.client.force_authenticate(self.admin)
        data = {'name': 'Plan 3', 'monthly_price': 300.0, 'benefits': self.benefit1.id}
        response = self.client.post(reverse('blog-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plan.objects.count(), 3)
        self.assertEqual(Plan.objects.get(name='Plan 3').monthly_price, 300.0)
        self.assertEqual(Plan.objects.get(name='Plan 3').benefits, self.benefit1)

    def test_create_plan_unauthenticated(self):
        data = {'name': 'Plan 3', 'monthly_price': 300.0, 'benefits': self.benefit1.id}
        response = self.client.post(reverse('blog-list'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Plan.objects.count(), 2)

    def test_create_plan_forbidden(self):
        self.client.force_authenticate(self.user)
        data = {'name': 'Plan 3', 'monthly_price': 300.0, 'benefits': self.benefit1.id}
        response = self.client.post(reverse('blog-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Plan.objects.count(), 2)

    def test_retrieve_plan(self):
        response = self.client.get(reverse('blog-list')+str(self.plan1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Plan 1')
        self.assertEqual(response.data['plan_benefits'][0]['details'], 'Benefit 1')
        self.assertEqual(response.data['price_per_month'], 100.0)
        self.assertEqual(response.data['price_per_year'], 1200.0)

    def test_update_plan(self):
        self.client.force_authenticate(self.admin)
        data = {'name': 'Plan 1 updated', 'monthly_price': 150.0, 'benefits': self.benefit2.id}
        response = self.client.put(reverse('blog-list')+str(self.plan1.id)+'/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Plan.objects.get(id=self.plan1.id).name, 'Plan 1 updated')
        self.assertEqual(Plan.objects.get(id=self.plan1.id).monthly_price, 150.0)
        self.assertEqual(Plan.objects.get(id=self.plan1.id).benefits, self.benefit2)

    def test_update_plan_unauthenticated(self):
        data = {'name': 'Plan 1 updated', 'monthly_price': 150.0, 'benefits': self.benefit2.id}
        response = self.client.put(reverse('blog-list')+str(self.plan1.id)+'/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Plan.objects.get(id=self.plan1.id).name, 'Plan 1')
        self.assertEqual(Plan.objects.get(id=self.plan1.id).monthly_price, 100.0)
        self.assertEqual(Plan.objects.get(id=self.plan1.id).benefits, self.benefit1)

    def test_update_plan_forbidden(self):
        self.client.force_authenticate(self.user)
        data = {'name': 'Plan 1 updated', 'monthly_price': 150.0, 'benefits': self.benefit2.id}
        response = self.client.put(reverse('blog-list')+str(self.plan1.id)+'/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Plan.objects.get(id=self.plan1.id).name, 'Plan 1')
        self.assertEqual(Plan.objects.get(id=self.plan1.id).monthly_price, 100.0)
        self.assertEqual(Plan.objects.get(id=self.plan1.id).benefits, self.benefit1)

    def test_delete_plan(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(reverse('blog-list')+str(self.plan1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Plan.objects.count(), 1)

    def test_delete_plan_unauthenticated(self):
        response = self.client.delete(reverse('blog-list')+str(self.plan1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Plan.objects.count(), 2)

    def test_delete_plan_forbidden(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse('blog-list')+str(self.plan1.id)+'/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Plan.objects.count(), 2)


class LinkedInLoginViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_linkedin_login(self):
        # create a test user
        user = User.objects.create_user(email='test@example.com', password='testpassword')

        # create a social account for the user
        SocialAccount.objects.create(user=user, provider='linkedin', uid='123')

        # simulate a valid access_token
        access_token = 'valid_access_token'

        # make a post request to the view
        response = self.client.post(reverse('linkedin_login'), {'access_token': access_token})

        # check that the response is successful
        self.assertEqual(response.status_code, 200)

        # check that the token and user_id are returned in the response
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['user_id'], user.id)
