from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Project

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Проект',
            surname='Тестов',
            password='pass123'
        )

    def test_create_project(self):
        project = Project.objects.create(
            name='Тестовый проект',
            description='Описание',
            owner=self.user,
            status='open'
        )
        self.assertEqual(project.name, 'Тестовый проект')
        self.assertEqual(project.status, 'open')
        self.assertEqual(project.owner, self.user)

    def test_project_str(self):
        project = Project.objects.create(
            name='Строковый тест',
            owner=self.user
        )
        self.assertEqual(str(project), 'Строковый тест')
