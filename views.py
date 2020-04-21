# Create your views here.
import csv
import io
from django.apps import apps
from django.db import IntegrityError
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from .forms import CSVUploadForm
from .utils import *


def create_model_instance_with_csv(model, cleaned_data):
    csv_file = cleaned_data.pop('csv_file')
    required_fields = get_required_fields(model)
    optional_fields = get_optional_fields(model)
    fk_fields = get_fk_fields(model)
    decoded_file = csv_file.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string, delimiter=',')
    for row in reader:
        fields_dict = {}
        for field in required_fields:
            if field in fk_fields:
                field = field + '_id'
            fields_dict[field] = row.get(field)
        for field in optional_fields:
            if field in fk_fields:
                fields_dict[field + '_id'] = row.get(field, None)
            else:
                val = row.get(field, None)
                if val == '':
                    val = None
                fields_dict[field] = val
        try:
            combined_fields = dict(fields_dict)
            combined_fields.update(cleaned_data)
            print(combined_fields)
            model_instance = model.objects.create(**combined_fields)
        except IntegrityError as e:
            raise e


def upload_csv(request, app_label, model_name):
    context = {}
    errors = {}
    model = apps.get_model(app_label, model_name)
    if request.method != 'POST':
        form = CSVUploadForm(model=model)
    else:
        form = CSVUploadForm(request.POST, request.FILES, model=model)
        if form.is_valid():
            try:
                create_model_instance_with_csv(model, form.cleaned_data)
                return redirect(reverse('admin:%s_%s_changelist' % (app_label, model_name)))
            except Exception as e:
                print(e)
                errors['error'] = e
                # self.message_user(request, 'Failure: ' + str(e), messages.ERROR)

    context['opts'] = model._meta
    context['form'] = form
    context['title'] = 'Upload .csv file with details'
    context['errors'] = errors
    return TemplateResponse(
        request,
        'upload_csv.html',
        context,
    )
