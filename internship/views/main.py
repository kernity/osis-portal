# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from base.views import layout
import base.models as mdl_base
import internship.models as mdl_internship
from internship.forms.form_select_speciality import SpecialityForm
from internship.forms.form_offer_preference import OfferPreferenceFormSet, OfferPreferenceForm
from django.forms import formset_factory


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
def view_internship_home(request):

    return layout.render(request, "internship_home.html")


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
def view_internship_selection(request, internship_id="1", speciality_id="-1"):
    NUMBER_NON_MANDATORY_INTERNSHIPS = 6
    student = mdl_base.student.find_by_user(request.user)

    is_open = mdl_internship.internship_offer.get_number_selectable() > 0
    if not is_open:
        return layout.render(request, "internship_selection_closed.html")

    speciality = mdl_internship.internship_speciality.find_by_id(speciality_id)
    selectable_offers = mdl_internship.internship_offer.find_selectable_by_speciality(speciality=speciality)
    offer_preference_formset = formset_factory(OfferPreferenceForm, formset=OfferPreferenceFormSet,
                                               extra=len(selectable_offers), min_num=len(selectable_offers),
                                               max_num=len(selectable_offers), validate_min=True, validate_max=True)
    formset = offer_preference_formset()

    if request.method == 'POST':
        formset = offer_preference_formset(request.POST)
        if formset.is_valid() and do_not_exceed_maximum_personnal_internship(speciality, student):
            remove_previous_choices(student, internship_id)
            save_student_choices(formset, student, int(internship_id), speciality)

    specialities = mdl_internship.internship_speciality.find_non_mandatory()
    number_first_choices_by_organization = get_first_choices_by_organization(speciality)

    return layout.render(request, "internship_selection.html",
                         {"number_non_mandatory_internships": range(1, NUMBER_NON_MANDATORY_INTERNSHIPS + 1),
                          "speciality_form": SpecialityForm(),
                          "all_specialities": specialities,
                          "formset": formset,
                          "offers_forms": zip_offers_formset_and_first_choices(formset, selectable_offers,
                                                                               number_first_choices_by_organization),
                          "speciality_id": int(speciality_id),
                          "intern_id": int(internship_id),
                          "can_submit": len(selectable_offers) > 0})


def get_first_choices_by_organization(speciality):
    list_number_choices = mdl_internship.internship_choice.get_number_first_choice_by_organization(speciality)
    dict_number_choices_by_organization = dict()
    for number_first_choices in list_number_choices:
        dict_number_choices_by_organization[number_first_choices["organization"]] = \
            number_first_choices["organization__count"]
    return dict_number_choices_by_organization


def zip_offers_formset_and_first_choices(formset, internships_offers, number_choices_by_organization):
    zipped_data = None
    if internships_offers:
        zipped_data = []
        for offer, form in zip(internships_offers, formset):
            zipped_data.append((offer, form, number_choices_by_organization.get(offer.organization.id, 0)))
    return zipped_data


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
def assign_speciality_for_internship(request, internship_id):
    speciality_id = None
    if request.method == "POST":
        speciality_id = int(request.POST.get("speciality_chosen", 0))

    return redirect("select_internship_speciality", internship_id=internship_id, speciality_id=speciality_id)


def remove_previous_choices(student, internship_id):
    previous_choices = mdl_internship.internship_choice.search(student, internship_id)
    if previous_choices:
        previous_choices.delete()


def save_student_choices(formset, student, internship_id, speciality):
    for form in formset:
        if form.cleaned_data:
            offer_pk = form.cleaned_data["offer"]
            preference_value = int(form.cleaned_data["preference"])
            offer = mdl_internship.internship_offer.find_by_pk(offer_pk)
            if has_been_selected(preference_value) and is_correct_speciality(offer, speciality):
                internship_choice = mdl_internship.internship_choice.InternshipChoice(student=student,
                                                                                      organization=offer.organization,
                                                                                      speciality=speciality,
                                                                                      choice=preference_value,
                                                                                      internship_choice=internship_id,
                                                                                      priority=False)
                internship_choice.save()


def has_been_selected(preference_value):
    return bool(preference_value)


def is_correct_speciality(offer, speciality):
    return offer.speciality == speciality


def do_not_exceed_maximum_personnal_internship(speciality, student):
    if speciality.acronym != "SP":
        return True
    number_choices_personal_internship = \
        mdl_internship.internship_choice.search(student=student, speciality=speciality).count()
    return number_choices_personal_internship < 2
