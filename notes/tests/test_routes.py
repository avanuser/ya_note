from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Title', text='Text', slug='text', author=cls.author
        )

    def test_home_page_for_anonymous(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        urls = (
            ('notes:home', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        self.client.force_login(self.author)    # залогиним автора
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_not_available_for_reader(self):
        url = reverse('notes:detail', kwargs={'slug': self.note.slug})
        self.client.force_login(self.reader)    # залогиним reader
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirects_for_anonymous_client(self):
        url = reverse('notes:detail', kwargs={'slug': self.note.slug})
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)
