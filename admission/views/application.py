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
from admission import models as mdl
from django.shortcuts import render, get_object_or_404
from reference import models as mdl_reference

from datetime import datetime
from admission.views.common import home
from functools import cmp_to_key
import locale
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from admission.views.common import extra_information


def applications(request):
    applications = mdl.application.find_by_user(request.user)
    return render(request, "home.html", {'applications': applications, 'tab_active': 3})


def application_update(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "offer_selection.html",
                           {"offers":             None,
                            "offer":              application.offer_year,
                            "application":        application,
                            "tab_demande_active": 0})


def profile_confirmed(request):
    return render(request, "profile_confirmed.html")


def save_application_offer(request):
    if request.method == 'POST' and 'save' in request.POST:
        applications = mdl.application.find_by_user(request.user)

        if applications is None or len(applications) == 0:
            # First demande perharps somme data to save
            person = mdl.person.find_by_user(request.user)
            if person is None:
                person = mdl.person.Person()
            if request.POST.get('nationality_first'):
                country_id = request.POST['nationality_first']
                country = mdl_reference.country.find_by_id(int(country_id))
                person.nationality = country
                person.birth_country = country
            else:
                person.nationality = None
            person.save()
            person_legal_address = mdl.person_address.find_by_person_type(person, 'LEGAL')

            if person_legal_address is None:
                person_legal_address = mdl.person_address.PersonAddress()
                person_legal_address.person = person
                person_legal_address.type = 'LEGAL'
            if request.POST.get('legal_adr_country'):
                country_id = request.POST['legal_adr_country']
                country = mdl_reference.country.find_by_id(int(country_id))
                person_legal_address.country = country
            else:
                person_legal_address.country = None
            person_legal_address.save()
            if request.POST.get('rdb_belgian_foreign'):
                secondary_education = mdl.secondary_education.find_by_person(person)
                if secondary_education is None:
                    secondary_education = mdl.secondary_education.SecondaryEducation()
                    secondary_education.person = person
                    if request.POST.get('rdb_belgian_foreign') == 'true':
                        secondary_education.national = True
                    else:
                        secondary_education.national = False
                secondary_education.save()

        #
        offer_year = None
        offer_year_id = request.POST.get('offer_year_id')

        application_id = request.POST.get('application_id')

        if application_id:
            application = get_object_or_404(mdl.application.Application, pk=application_id)
            secondary_education = mdl.secondary_education.find_by_person(application.person)
        else:
            application = mdl.application.Application()
            person_application = mdl.person.find_by_user(request.user)
            application.person = person_application
            secondary_education = mdl.secondary_education.SecondaryEducation()
            secondary_education.person = application.person

        if secondary_education.academic_year is None:
            secondary_education.academic_year = mdl.academic_year.current_academic_year()

        if offer_year_id:
            offer_year = mdl.offer_year.find_by_id(offer_year_id)
            if offer_year.grade_type:
                if offer_year.grade_type.grade == 'DOCTORATE':
                    application.doctorate = True
                else:
                    application.doctorate = False

        application.offer_year = offer_year

        if request.POST.get('rdb_offer_belgiandegree'):
            if request.POST.get('rdb_offer_belgiandegree') == "true":
                application.belgian_degree = True
            else:
                application.belgian_degree = False
        if request.POST.get('rdb_offer_vae'):
            if request.POST.get('rdb_offer_vae') == "true":
                application.vae = True
            else:
                application.vae = False
        if request.POST.get('rdb_offer_samestudies'):
            if request.POST.get('rdb_offer_samestudies') == "true":
                application.started_samestudies = True
            else:
                application.started_samestudies = False
        if request.POST.get('rdb_offer_valuecredits'):
            if request.POST.get('rdb_offer_valuecredits') == "true":
                application.credits_to_value = True
            else:
                application.credits_to_value = False
        if request.POST.get('rdb_offer_sameprogram'):
            if request.POST.get('rdb_offer_sameprogram') == "true":
                application.applied_to_sameprogram = True
            else:
                application.resident = False
        if request.POST.get('rdb_offer_resident'):
            if request.POST.get('rdb_offer_resident') == "true":
                application.resident = True
            else:
                application.resident = False
        if request.POST.get('txt_offer_lottery'):
            application.lottery_number = request.POST.get('txt_offer_lottery')

        application.save()
        # answer_question_
        for key, value in request.POST.items():
            if "txt_answer_question_" in key:
                answer = mdl.answer.Answer()
                answer.application = application
                answer.value = value
                # as it's txt_answer we know that it's there is only one option available,
                # (SHORT_INPUT_TEXT, LONG_INPUT_TEXT)
                option_id = key.replace("txt_answer_question_", "")
                answer.option = mdl.option.find_by_id(int(option_id))
                answer.save()
            else:
                if "txt_answer_radio_chck_optid_" in key:

                    # RADIO_BUTTON
                    if "on" == value:
                        answer = mdl.answer.Answer()
                        answer.application = application
                        option_id = key.replace("txt_answer_radio_chck_optid_", "")
                        option = mdl.option.find_by_id(int(option_id))
                        answer.option = option
                        answer.value = option.value
                        answer.save()
                else:
                    if "slt_question_" in key:
                        answer = mdl.answer.Answer()
                        answer.application = application
                        option = mdl.option.find_by_id(value)
                        answer.option = option
                        answer.value = option.value
                        answer.save()
        return HttpResponseRedirect(reverse('home'))
        # print(application.id)
        # return HttpResponseRedirect(reverse('demande_update'), kwargs={'application_id': application.id})
        # return HttpResponseRedirect(reverse('demande_update'), args=(application.id))


def application_view(request, application_id):
    application = mdl.application.find_by_id(application_id)
    answers = mdl.answer.find_by_application(application_id)
    return render(request, "application.html",
                           {"application": application,
                            "answers": answers})


def application_delete(request, application_id):
    application = mdl.application.find_by_id(application_id)
    application.delete()
    return HttpResponseRedirect(reverse('home'))


def submission(request, application_id=None):
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    return render(request, "demande_submission.html",
                  {'application':            application,
                   'tab_demande_active':     1,
                   'tab_demande_active':     2,
                   'display_admission_exam': extra_information(request, application)})
