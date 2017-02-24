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
from django.utils.translation import ugettext_lazy as _
from osis_common.models.serializable_model import SerializableModel


class PersonAddressAdmin(admin.ModelAdmin):
    list_display = ('person', 'type', 'street', 'postal_code', 'city', 'country')
    fieldsets = ((None, {'fields': ('person', 'type', 'street', 'postal_code', 'city', 'country')}),)


class PersonAddress(SerializableModel):
    ADDRESS_TYPE = (('LEGAL', _('Legal')),
                    ('CONTACT', _('Contact')))

    person = models.ForeignKey('Applicant')
    type = models.CharField(max_length=20, choices=ADDRESS_TYPE)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=6)
    complement = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.ForeignKey('reference.Country')


def find_by_person(a_person):
    """ Return a list containing one or more addresses of a person. Returns None if there is no address.
    :param a_person: An instance of the class base.models.person.Person
    """
    return PersonAddress.objects.filter(person=a_person)


def find_by_person_type(a_person, type):
    """ Return a list containing one or more addresses of a person. Returns None if there is no address.
    :param a_person: An instance of the class base.models.person.Person
    :param type
    """
    addresses = PersonAddress.objects.filter(person=a_person, type=type)
    if addresses:
        return addresses[0]
    return None
