from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestPages(TestCase):

    url = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(
            title='Title', text='Text', slug='text', author=cls.author
        )

    def check_form(self, test_data):
        for name, args, form in test_data:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], form)

    def test_authorized_client_has_forms(self):
        test_data = [
            ('notes:add', None, NoteForm),
            ('notes:edit', (self.note.slug,), NoteForm),
        ]
        self.client.force_login(self.author)    # залогиним автора
        self.check_form(test_data)

    def test_anonimous_has_forms(self):
        test_data = [
            ('users:login', None, AuthenticationForm),
            ('users:signup', None, UserCreationForm),
        ]
        self.check_form(test_data)
