# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipoffer',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, null=True),
        ),
        migrations.AddField(
            model_name='internshipspeciality',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, null=True),
        ),
    ]
