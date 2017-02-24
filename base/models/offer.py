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
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from base.models import offer_enrollment


class OfferAdmin(SerializableModelAdmin):
    fieldsets = ((None, {'fields': ('title',)}),)
    search_fields = ['title']


class Offer(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


def find_by_id(offer_id):
    return Offer.objects.get(pk=offer_id)


def find_by_student(student):
    offer_ids = offer_enrollment.find_by_student(student).values('offer_year__offer_id')
    return Offer.objects.filter(pk__in=offer_ids)
