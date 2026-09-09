# Notable

A simple notes app built with Django and a REST API (via [django-tastypie](https://django-tastypie.readthedocs.io/)), with a small vanilla-JS frontend.

## Features

- REST API for notes (create, read, update, delete)
- Minimal frontend using plain HTML/CSS/JS (`fetch`, no frameworks)
- SQLite database, Django admin enabled

## Tech stack

- Python / Django
- django-tastypie (API layer)
- SQLite
- Vanilla JavaScript (frontend)

## Setup

```bash
git clone <this-repo-url>
cd notable_django
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open `http://localhost:8000/` in your browser.

A local secret key is generated automatically on first run (stored in `.django_secret_key`, not committed). For a real deployment, set the `DJANGO_SECRET_KEY` environment variable instead.

## API

| Method | URL              | Description        |
|--------|------------------|---------------------|
| GET    | `/api/note/`     | List all notes      |
| POST   | `/api/note/`     | Create a note       |
| GET    | `/api/note/<id>/`| Get one note        |
| PUT    | `/api/note/<id>/`| Update one note     |
| DELETE | `/api/note/<id>/`| Delete one note     |

Example request body for creating a note:

```json
{
  "title": "My Note",
  "body": "Some content"
}
```
