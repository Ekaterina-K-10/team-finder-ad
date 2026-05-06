from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            name='Имя',
            surname='Фамилия',
            password='pass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertIsNotNone(user.password)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            name='Админ',
            surname='Админов',
            password='admin123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
