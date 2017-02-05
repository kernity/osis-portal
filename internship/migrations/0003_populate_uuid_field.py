# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import FieldDoesNotExist
from django.db import migrations, models
import uuid


def set_uuid_field(apps, schema_editor):
    """
    Set a random uuid value to all existing rows in all models containing an 'uuid' attribute in database.
    """
    base = apps.get_app_config('internship')
    for model_class in base.get_models():
        ids = model_class.objects.values_list('id', flat=True)
        if ids:
            for pk in ids:
                try:
                    model_class.objects.filter(pk=pk).update(uuid=uuid.uuid4())
                except FieldDoesNotExist:
                    break


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0002_add_uuid_field'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field),
        migrations.AlterField(
            model_name='internshipoffer',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='internshipspeciality',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
