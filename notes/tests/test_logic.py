from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import *
from notes.models import *

User = get_user_model()


class TestNoteCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода,
    # запишем его в атрибуты класса.
    NOTE_TEXT = 'Текст комментария'
    NOTE_TITLE = 'Заголовок комментария'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        # Адрес страницы с новостью.
        cls.url = reverse('notes:add')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {'text': cls.NOTE_TEXT, 'title': cls.NOTE_TITLE}

    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        comments_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(comments_count, 0)

    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл на нужную страницу.
        url = reverse('notes:success')
        self.assertRedirects(response, url)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        db_note = Note.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        self.assertEqual(db_note.text, self.NOTE_TEXT)
        self.assertEqual(db_note.title, self.NOTE_TITLE)
        self.assertEqual(db_note.author, self.author)


class TestNoteEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать 
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls, 
    # поэтому их можно перечислить просто в атрибутах класса.
    NOTE_TEXT = 'Старый текст'
    NEW_NOTE_TEXT = 'Новый текст'
    TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя - автора комментария, логиним.
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаём заметку в БД.
        cls.note = Note.objects.create(
            title=cls.TITLE, text=cls.NOTE_TEXT, slug='text', author=cls.author
        )
        # Формируем адрес блока с заметками, который понадобится для тестов.
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        # URL для редактирования заметки.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления заметки.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Формируем данные для POST-запроса по обновлению заметки.
        cls.form_data = {'title': cls.TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        url = reverse('notes:success')
        self.assertRedirects(response, url)
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_note(self):
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что код - 200.
        # self.assertEqual(response.status_code, HTTPStatus.OK)
        url = reverse('notes:success')
        self.assertRedirects(response, url)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
