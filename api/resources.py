from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.validation import Validation

from api.models import Note

TITLE_MAX_LENGTH = Note._meta.get_field('title').max_length


class NoteValidation(Validation):
    """Rejects notes without a title or with a title that is too long."""

    def is_valid(self, bundle, request=None):
        errors = {}
        title = (bundle.data.get('title') or '').strip()
        if not title:
            errors['title'] = 'Title is required.'
        elif len(title) > TITLE_MAX_LENGTH:
            errors['title'] = f'Title must be at most {TITLE_MAX_LENGTH} characters.'
        return errors


class NoteResource(ModelResource):
    class Meta:
        queryset = Note.objects.all()
        resource_name = 'note'
        fields = ['id', 'title', 'body', 'created_at', 'updated_at']
        allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
        # Open API with no login: fine for a local notes app, not for a shared deployment.
        authorization = Authorization()
        validation = NoteValidation()
        always_return_data = True  # POST/PUT answer with the saved note, so the UI needs no extra GET
        filtering = {'title': ['icontains']}
        ordering = ['created_at', 'updated_at', 'title']
        limit = 100

    def hydrate_title(self, bundle):
        if 'title' in bundle.data and bundle.data['title'] is not None:
            bundle.data['title'] = bundle.data['title'].strip()
        return bundle
