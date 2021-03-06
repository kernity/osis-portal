##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from django.db import models
from django.utils import timezone
from django.db.models import Q


class PropositionOfferAdmin(SerializableModelAdmin):
    list_display = ('proposition_dissertation', 'offer_proposition')
    raw_id_fields = ('proposition_dissertation', 'offer_proposition')
    search_fields = ('uuid', 'proposition_dissertation__title', 'offer_proposition__acronym',
                     'proposition_dissertation__author__person__last_name',
                     'proposition_dissertation__author__person__first_name')


class PropositionOffer(SerializableModel):
    proposition_dissertation = models.ForeignKey('PropositionDissertation')
    offer_proposition = models.ForeignKey('OfferProposition')

    def __str__(self):
        return str(self.offer_proposition)


def find_by_offers(offers):
    return PropositionOffer.objects.filter(proposition_dissertation__active=True,
                                           proposition_dissertation__visibility=True,
                                           offer_proposition__offer__in=offers,
                                           offer_proposition__start_visibility_proposition__lte=timezone.now(),
                                           offer_proposition__end_visibility_proposition__gte=timezone.now()
                                           )


def find_by_offers_ordered_by_proposition_dissertation(offers):
    return find_by_offers(offers).order_by('proposition_dissertation')


def search_by_proposition_dissertation(proposition_dissertation):
    return PropositionOffer.objects.filter(proposition_dissertation=proposition_dissertation)


def search(offers, terms, active=None, visibility=None):
    queryset = PropositionOffer.objects.filter(proposition_dissertation__active=True,
                                               proposition_dissertation__visibility=True,
                                               offer_proposition__offer__in=offers,
                                               offer_proposition__start_visibility_proposition__lte=timezone.now())\
        .distinct()
    if terms:
        queryset = queryset.filter(
            Q(proposition_dissertation__title__icontains=terms) |
            Q(proposition_dissertation__description__icontains=terms) |
            Q(proposition_dissertation__author__person__first_name__icontains=terms) |
            Q(proposition_dissertation__author__person__middle_name__icontains=terms) |
            Q(proposition_dissertation__author__person__last_name__icontains=terms) |
            Q(offer_proposition__acronym__icontains=terms)
        )
    if active:
        queryset = queryset.filter(proposition_dissertation__active=active)
    elif visibility:
        queryset = queryset.filter(proposition_dissertation__visibility=visibility)
    queryset = queryset.distinct()
    return queryset
