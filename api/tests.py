import json

from django.test import TestCase

from api.models import Note

LIST_URL = '/api/note/'


def detail_url(note_id):
    return f'{LIST_URL}{note_id}/'


class NoteApiTests(TestCase):
    def post_json(self, url, data):
        return self.client.post(url, json.dumps(data), content_type='application/json')

    def put_json(self, url, data):
        return self.client.put(url, json.dumps(data), content_type='application/json')

    def test_list_is_empty_at_start(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['objects'], [])

    def test_create_returns_the_saved_note(self):
        response = self.post_json(LIST_URL, {'title': 'Shopping', 'body': 'milk, eggs'})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['title'], 'Shopping')
        self.assertEqual(data['body'], 'milk, eggs')
        self.assertIn('created_at', data)
        self.assertEqual(Note.objects.count(), 1)

    def test_title_is_trimmed(self):
        response = self.post_json(LIST_URL, {'title': '  Exam  ', 'body': ''})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Note.objects.get().title, 'Exam')

    def test_missing_title_is_rejected(self):
        response = self.post_json(LIST_URL, {'body': 'no title'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['note'])
        self.assertEqual(Note.objects.count(), 0)

    def test_blank_title_is_rejected(self):
        response = self.post_json(LIST_URL, {'title': '   ', 'body': 'x'})
        self.assertEqual(response.status_code, 400)

    def test_too_long_title_is_rejected(self):
        response = self.post_json(LIST_URL, {'title': 'a' * 201, 'body': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Note.objects.count(), 0)

    def test_get_one_note(self):
        note = Note.objects.create(title='One', body='first')
        response = self.client.get(detail_url(note.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'One')

    def test_unknown_note_is_404(self):
        response = self.client.get(detail_url(999))
        self.assertEqual(response.status_code, 404)

    def test_update_changes_title_and_body(self):
        note = Note.objects.create(title='Old', body='old body')
        response = self.put_json(detail_url(note.id), {'title': 'New', 'body': 'new body'})
        self.assertEqual(response.status_code, 200)
        note.refresh_from_db()
        self.assertEqual((note.title, note.body), ('New', 'new body'))

    def test_update_with_blank_title_is_rejected(self):
        note = Note.objects.create(title='Keep me', body='')
        response = self.put_json(detail_url(note.id), {'title': '', 'body': ''})
        self.assertEqual(response.status_code, 400)
        note.refresh_from_db()
        self.assertEqual(note.title, 'Keep me')

    def test_delete_removes_the_note(self):
        note = Note.objects.create(title='Bye', body='')
        response = self.client.delete(detail_url(note.id))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Note.objects.exists())

    def test_list_is_newest_first(self):
        first = Note.objects.create(title='first', body='')
        second = Note.objects.create(title='second', body='')
        # created in the same instant on fast machines, so set the order explicitly
        Note.objects.filter(pk=first.pk).update(created_at='2026-01-01T10:00:00Z')
        Note.objects.filter(pk=second.pk).update(created_at='2026-01-02T10:00:00Z')
        titles = [n['title'] for n in self.client.get(LIST_URL).json()['objects']]
        self.assertEqual(titles, ['second', 'first'])

    def test_filter_by_title(self):
        Note.objects.create(title='Java exam', body='')
        Note.objects.create(title='Groceries', body='')
        response = self.client.get(LIST_URL, {'title__icontains': 'java'})
        titles = [n['title'] for n in response.json()['objects']]
        self.assertEqual(titles, ['Java exam'])


class IndexPageTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Notes</h1>', html=True)
