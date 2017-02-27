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
from reference import models as mdl_reference
from datetime import datetime, timedelta


PROFIL_INSCRIPTION = 'PROFIL_INSCRIPTION'
PROFIL_INSCRIPTION_DOCTORAT = 'PROFIL_INSCRIPTION_DOCTORAT'
PROFIL_ADMISSION_DOCTORAT = 'PROFIL_ADMISSION_DOCTORAT'
PROFIL_ADMISSION_HORS_UE_RESIDENT = 'PROFIL_ADMISSION_HORS_UE_RESIDENT'
PROFIL_ADMISSION_HORS_UE_NON_RESIDENT = 'PROFIL_ADMISSION_HORS_UE_NON_RESIDENT'
PROFIL_ADMISSION_DIPL_ETR_NATIONALITE_BELGE = 'PROFIL_ADMISSION_DIPL_ETR_NATIONALITE_BELGE'
PROFIL_ADMISSION_UE_RESIDENT = 'PROFIL_ADMISSION_UE_RESIDENT'
PROFIL_ADMISSION_UE_NON_RESIDENT = 'PROFIL_ADMISSION_UE_NON_RESIDENT'
PROFIL_INDERTERMINE = 'PROFIL_INDERTERMINE'


CODE_FONCTION_DATE_CLOTURE_INSCRIPTION = 'DATE_CLOTURE_INSCRIPTION'
CODE_FONCTION_DATE_CLOTURE_ADMISSION_HORS_UE_RESIDENT = 'DATE_CLOTURE_ADMISSION_HORS_UE_RESIDENT'
CODE_FONCTION_DATE_CLOTURE_ADMISSION_HORS_UE_NON_RESIDENT = 'DATE_CLOTURE_ADMISSION_HORS_UE_NON_RESIDENT'
CODE_FONCTION_DATE_CLOTURE_ADMISSION_DIPL_ETR_NATIONALITE_BELGE = 'DATE_CLOTURE_ADMISSION_DIPL_ETR_NAT_BELGE'
CODE_FONCTION_DATE_CLOTURE_ADMISSION_UE_RESIDENT = 'DATE_CLOTURE_ADMISSION_UE_RESIDENT'
CODE_FONCTION_DATE_CLOTURE_ADMISSION_UE_NON_RESIDENT = 'DATE_CLOTURE_ADMISSION_UE_NON_RESIDENT'
CODE_FONCTION_DATE_LIMITE_ENVOI_ADMISSION_HORS_UE_NON_RESIDENT = 'DATE_LIMITE_ENVOI_ADMISSION_HORS_UE_NON_RESIDENT'
CODE_FONCTION_DATE_LIMITE_ENVOI_ADMISSION_UE_NON_RESIDENT = 'DATE_LIMITE_ENVOI_ADMISSION_UE_NON_RESIDENT'


def get_limit_sending_date(an_application, an_applicant):
    doctorate = False
    if an_application.offer_year.grade_type.institutional_grade_type == "DOCTORATE":
        doctorate = True
    belgian_nationality = False
    if an_applicant.nationality == mdl_reference.country.find_by_iso_code("BE"):
        belgian_nationality = True
    belgian_diploma = False
    if an_application.coverage_access_degree == "NATIONAL":
        belgian_diploma = True
    profil = get_applicant_profil(doctorate,
                                  belgian_nationality,
                                  an_applicant.nationality.european_union,
                                  an_application.resident,
                                  belgian_diploma)
    sending_ultimate_date = get_sending_limit_date(profil, an_application.submission_date)
    plus_one_month = an_application.submission_date + timedelta(days=30)
    if plus_one_month > sending_ultimate_date:
        return sending_ultimate_date.strftime('%d/%m/%Y')
    return plus_one_month.strftime('%d/%m/%Y')


def get_applicant_profil(doctorate, belgian_nationality, european_union, resident, belgian_diploma):
    if doctorate is None or belgian_nationality is None or european_union is None or resident is None or belgian_diploma:
        return PROFIL_INDERTERMINE

    if belgian_diploma and (belgian_nationality or european_union):
        if doctorate:
            applicant_profil = PROFIL_INSCRIPTION_DOCTORAT
        else:
            applicant_profil = PROFIL_INSCRIPTION
    elif doctorate:
        applicant_profil = PROFIL_ADMISSION_DOCTORAT
    elif not belgian_diploma and belgian_nationality:
        applicant_profil = PROFIL_ADMISSION_DIPL_ETR_NATIONALITE_BELGE
    elif european_union:
        if resident:
            applicant_profil = PROFIL_ADMISSION_UE_RESIDENT
        else:
            applicant_profil = PROFIL_ADMISSION_UE_NON_RESIDENT
    else:
        if resident:
            applicant_profil = PROFIL_ADMISSION_HORS_UE_RESIDENT
        else:
            applicant_profil = PROFIL_ADMISSION_HORS_UE_NON_RESIDENT

    return applicant_profil


def get_sending_limit_date(profil, submission_date):
    if profil == PROFIL_ADMISSION_HORS_UE_NON_RESIDENT:
        return get_date_by_profil(CODE_FONCTION_DATE_LIMITE_ENVOI_ADMISSION_HORS_UE_NON_RESIDENT)

    if profil == PROFIL_ADMISSION_UE_NON_RESIDENT:
        return get_date_by_profil(CODE_FONCTION_DATE_LIMITE_ENVOI_ADMISSION_UE_NON_RESIDENT)

    return get_closure_date(profil, submission_date)


def get_closure_date(applicant_profil, submission_date):
    if applicant_profil == PROFIL_INSCRIPTION:
        return get_date_by_profil(CODE_FONCTION_DATE_CLOTURE_INSCRIPTION)

    if applicant_profil == PROFIL_ADMISSION_HORS_UE_RESIDENT:
        return get_date_by_profil(CODE_FONCTION_DATE_CLOTURE_ADMISSION_HORS_UE_RESIDENT)

    if applicant_profil == PROFIL_ADMISSION_HORS_UE_NON_RESIDENT:
        return get_date_by_profil(CODE_FONCTION_DATE_CLOTURE_ADMISSION_HORS_UE_NON_RESIDENT)

    if applicant_profil == PROFIL_ADMISSION_DIPL_ETR_NATIONALITE_BELGE:
        return get_date_by_profil(CODE_FONCTION_DATE_CLOTURE_ADMISSION_DIPL_ETR_NATIONALITE_BELGE)

    if applicant_profil == PROFIL_ADMISSION_UE_RESIDENT:
        return get_date_by_profil(CODE_FONCTION_DATE_CLOTURE_ADMISSION_UE_RESIDENT)

    if applicant_profil == PROFIL_ADMISSION_UE_NON_RESIDENT:
        return get_date_by_profil(CODE_FONCTION_DATE_CLOTURE_ADMISSION_UE_NON_RESIDENT)

    return submission_date + timedelta(days=30)


def get_date_by_profil(code_fonction):
    # a compléter
    return datetime.datetime.now()

