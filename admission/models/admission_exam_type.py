##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db import models
from django.contrib import admin
from osis_common.models.serializable_model import SerializableModel


class AdmissionExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'adhoc')


class AdmissionExamType(SerializableModel):
    name = models.CharField(max_length=100)
    adhoc = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def find_by_name(a_name):
    return AdmissionExamType.objects.filter(name__iexact=a_name, adhoc=True).first()


def find_all_by_adhoc(an_adhoc):
    return AdmissionExamType.objects.filter(adhoc=an_adhoc).order_by('-adhoc', 'name')


def find_by_id(an_id):
    return AdmissionExamType.objects.get(pk=an_id)