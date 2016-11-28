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
from django.utils.translation import ugettext_lazy as _
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from admission import models as mdl
from admission.views import accounting
from admission.models.enums import application_type
from osis_common import models as mdl_common
from reference.enums import institutional_grade_type as enum_institutional_grade_type
from osis_common.messaging import send_message


VARIABLE_ENROLLMENT_UNEMPLOYMENT_DOC = 'unemployment_doc'
VARIABLE_ENROLLMENT_DEBTS_DOC = 'debts_doc'
VARIABLE_ENROLLMENT_OTHER_ACTIVITIES_DOC = 'other_activity_doc'
VARIABLE_ENROLLMENT_OFFER_ACRONYM = 'offer_acronym'
VARIABLE_ENROLLMENT_SECONDARY_DIPLOMA_DOC = 'secondary_diploma_doc'
VARIABLE_ENROLLMENT_EXAM_ADMISSION_DOC = 'exam_admission_doc'
VARIABLE_ENROLLMENT_CAPAES_DOC = 'capaes_doc'
VARIABLE_ENROLLMENT_CAPAES_IDENTIFICATION_DOC = 'capaes_identification_doc'
VARIABLE_ENROLLMENT_OPES_DOC = 'opes_doc'
VARIABLE_ENROLLMENT_FOPA_DOC = 'fopa_doc'
VARIABLE_ENROLLMENT_CAPAES_DATES = 'capaes_dates'

VARIABLE_CLOSING_DATE = 'closing_date'
VARIABLE_ORGANIZATION_COUNTRY = 'organization_country'
VARIABLE_ORGANIZATION_CITY = 'organization_city'
VARIABLE_ORGANIZATION_STREET = 'organization_street'
VARIABLE_ORGANIZATION_NAME = 'organization_name'
VARIABLE_RESPONSIBLE = 'responsible'
VARIABLE_SUBJECT_TO_QUOTA_TXT_3 = 'subject_to_quota_txt3'
VARIABLE_SUBJECT_TO_QUOTA_TXT_2 = 'subject_to_quota_txt2'
VARIABLE_SUBJECT_TO_QUOTA_TXT_1 = 'subject_to_quota_txt1'
VARIABLE_ADMISSION_ACADEMIC_YEAR = 'academic_year'
VARIABLE_ADMISSION_URL_EN = 'url_en'
VARIABLE_ADMISSION_URL_FR = 'url_fr'
VARIABLE_TITLE = 'title'
VARIABLE_REFERENCE = 'reference'
VARIABLE_FIRST_NAME = 'first_name'
VARIABLE_LAST_NAME = 'last_name'
VARIABLE_ENROLLMENT_YEAR = 'year'

UNEMPLOYMENT_DOC_NEEDED_TXT = 'onem_doc_needed'
DEBTS_DOC_NEEDED_TXT = 'debts_doc_needed'
OTHER_DOC_NEEDED_TXT = 'other_doc_needed'
SECONDARY_DIPLOMA_DOC_NEEDED_TXT = 'secondary_diploma_doc_needed'
SECONDARY_DIPLOMA_NEEDED_TXT = 'secondary_diploma_needed'


EXAM_ADMISSION_DOC_NEEDED_TXT = 'exam_admission_doc_needed'
SPECIAL_EXAM_ADMISSION_NEEDED_TXT = 'special_exam_admission_doc_needed'
CAPAES_DOC_NEEDED_TXT = 'capaes_doc_needed'
CAPAES_IDENTIFICATION_DOC_NEEDED_TXT = 'capaes_identification_doc_needed'
OPES_URL_TXT = 'opes_url'
FOPA_URL_TXT = 'fopa_url'

ENGLISH_URL_PREFIX = "en-"
MODEL_ADMISSION = "submission_admission"
MODEL_INSCRIPTON = "submission_inscription"


def get_submission_docs_url(grade_type):
    if grade_type:
        url_info_fr = check_format_url(grade_type.url_info)
        if url_info_fr:
            return [url_info_fr, build_english_url(url_info_fr)]
    return None


def get_submission_docs_url_fr(a_grade_type):
    if a_grade_type:
        url_info_fr = check_format_url(a_grade_type.url_info)
        if url_info_fr:
            return url_info_fr
    return ""


def get_submission_docs_url_en(a_grade_type):
    if a_grade_type:
        url_info_fr = check_format_url(a_grade_type.url_info)
        if url_info_fr:
            return build_english_url(url_info_fr)
        return ""


def check_format_url(url_info):
    if url_info:
        url_info = url_info.strip()
        if len(url_info) == 0:
            return None
        else:
            if valid_existing_url(url_info):
                return url_info
    return None


def valid_existing_url(url_info):

    my_url_validator = URLValidator()

    try:
        my_url_validator(url_info)
        return True
    except ValidationError:
        return False


def build_english_url(url_info_fr):
    position_last_slash = str.rfind(url_info_fr, '/')
    if position_last_slash > 0:
        part_1 = url_info_fr[0:position_last_slash+1]
        part_2 = url_info_fr[position_last_slash+1:len(url_info_fr)]
        return "{0}{1}{2}".format(part_1, ENGLISH_URL_PREFIX, part_2)
    return ""


def get_title(applicant):
    if applicant.gender == mdl.applicant.MALE:
        return _('mister')
    if applicant.gender == mdl.applicant.FEMALE:
        if applicant.civil_status != mdl.applicant.MARRIED:
            return _('ms')
        else:
            return _('madam')
    return "{0}, {1}".format(_('madam'), _('mister'))


def find_model_reference(an_application_type):
    if an_application_type == application_type.ADMISSION:
        return MODEL_ADMISSION
    if an_application_type == application_type.INSCRIPTION:
        return MODEL_INSCRIPTON
    return None


def get_model_message(an_application_type):
    model_message_reference = find_model_reference(an_application_type)
    if model_message_reference:
        model_messages = mdl_common.message_template.find_by_reference(model_message_reference)
        if model_messages.exists():
            return model_messages[0]
    return None


def message_template_admission_variables(an_applicant, an_application):
    data = {VARIABLE_LAST_NAME: an_applicant.user.last_name,
            VARIABLE_FIRST_NAME: an_applicant.user.first_name,
            VARIABLE_REFERENCE: '',
            VARIABLE_TITLE: get_title(an_applicant),
            VARIABLE_ADMISSION_URL_FR: get_submission_docs_url_fr(an_application.offer_year.grade_type),
            VARIABLE_ADMISSION_URL_EN: get_submission_docs_url_en(an_application.offer_year.grade_type),
            VARIABLE_ADMISSION_ACADEMIC_YEAR: get_academic_year(an_application.offer_year.academic_year.year),
            VARIABLE_SUBJECT_TO_QUOTA_TXT_1:
                get_subject_to_quota_txt_part(an_application.offer_year.subject_to_quota, 1),
            VARIABLE_SUBJECT_TO_QUOTA_TXT_2:
                get_subject_to_quota_txt_part(an_application.offer_year.subject_to_quota, 2),
            VARIABLE_SUBJECT_TO_QUOTA_TXT_3:
                get_subject_to_quota_txt_part(an_application.offer_year.subject_to_quota, 3),
            VARIABLE_RESPONSIBLE: '',
            VARIABLE_ORGANIZATION_NAME: '',
            VARIABLE_ORGANIZATION_STREET: '',
            VARIABLE_ORGANIZATION_CITY: '',
            VARIABLE_ORGANIZATION_COUNTRY: '',
            VARIABLE_CLOSING_DATE: ''}
    return data


def get_academic_year(a_year):
    if a_year:
        year_plus_one = a_year + 1
        return "{0}-{1}".format(str(a_year), str(year_plus_one))
    return ""


def send_soumission_email():
    return None


def get_subject_to_quota_txt_part(subject_to_quota, sequence_number):
    if subject_to_quota is True:
        return _("{0}{1}".format('subject_to_quota_txt_part', sequence_number))
    return ""


def message_template_inscription_variables(an_applicant, an_application):
    data = {VARIABLE_LAST_NAME: an_applicant.user.last_name,
            VARIABLE_FIRST_NAME: an_applicant.user.first_name,
            VARIABLE_REFERENCE: '',
            VARIABLE_ENROLLMENT_OFFER_ACRONYM: an_application.offer_year.acronym,
            VARIABLE_TITLE: get_title(an_applicant),
            VARIABLE_ENROLLMENT_YEAR: an_application.offer_year.academic_year.year,
            VARIABLE_SUBJECT_TO_QUOTA_TXT_1: get_subject_to_quota_txt_part(an_application.offer_year.subject_to_quota,
                                                                           1),
            VARIABLE_SUBJECT_TO_QUOTA_TXT_2: get_subject_to_quota_txt_part(an_application.offer_year.subject_to_quota,
                                                                           2),
            VARIABLE_SUBJECT_TO_QUOTA_TXT_3: get_subject_to_quota_txt_part(an_application.offer_year.subject_to_quota,
                                                                           3),
            VARIABLE_RESPONSIBLE: '',
            VARIABLE_ORGANIZATION_NAME: '',
            VARIABLE_ORGANIZATION_STREET: '',
            VARIABLE_ORGANIZATION_CITY: '',
            VARIABLE_ORGANIZATION_COUNTRY: '',
            VARIABLE_CLOSING_DATE: '',
            VARIABLE_ENROLLMENT_UNEMPLOYMENT_DOC: get_message_document(an_applicant, 'UNEMPLOYMENT'),
            VARIABLE_ENROLLMENT_DEBTS_DOC: get_debts_document(an_application),
            VARIABLE_ENROLLMENT_OTHER_ACTIVITIES_DOC: get_other_activity_type_document(an_applicant),
            VARIABLE_ENROLLMENT_SECONDARY_DIPLOMA_DOC: get_message_secondary_diploma_document(an_applicant),
            VARIABLE_ENROLLMENT_EXAM_ADMISSION_DOC: get_message_exam_admission_document(an_applicant, an_application),
            VARIABLE_ENROLLMENT_CAPAES_DOC:
                get_message_capaes_document(an_application.offer_year.grade_type.institutional_grade_type),
            VARIABLE_ENROLLMENT_CAPAES_IDENTIFICATION_DOC:
                get_message_capaes_identification_document(
                    an_application.offer_year.grade_type.institutional_grade_type),
            VARIABLE_ENROLLMENT_OPES_DOC: get_opes_url(an_application.offer_year.acronym),
            VARIABLE_ENROLLMENT_FOPA_DOC: get_fopa_url(an_application.offer_year.acronym),
            VARIABLE_ENROLLMENT_CAPAES_DATES:
                get_capaes_dates_paragraph(an_application.offer_year.grade_type.institutional_grade_type,
                                           an_application.offer_year.academic_year.year)}
    return data


def get_message_document(an_applicant, an_activity_type):
    curriculum_list = mdl.curriculum.search(an_applicant, an_activity_type)
    if curriculum_list.exists():
        return UNEMPLOYMENT_DOC_NEEDED_TXT
    return ""


def get_debts_document(an_application):
    if accounting.debts_check(an_application):
        return _(DEBTS_DOC_NEEDED_TXT)
    return ""


def get_other_activity_type_document(an_applicant):
    curriculum_list = mdl.curriculum.search(an_applicant, 'OTHER', None)
    return build_messages(curriculum_list)


def build_messages(curriculum_list):
    if curriculum_list.exists():
        msg = ""
        for cv in curriculum_list:
            msg = msg + " {0} {1}".format(_(OTHER_DOC_NEEDED_TXT), get_academic_year(cv.academic_year))
        return msg
    return ""


def get_message_studies_document(an_applicant):
    curriculum_list = mdl.curriculum.find_by_path_type_list(an_applicant,
                                                            ['LOCAL_UNIVERSITY',
                                                             'FOREIGN_UNIVERSITY',
                                                             'LOCAL_HIGH_EDUCATION',
                                                             'FOREIGN_HIGH_EDUCATION'])
    return build_messages(curriculum_list)


def get_message_exam_admission_document(an_applicant, an_application):
    a_secondary_education = mdl.secondary_education.find_by_person(an_applicant)
    if a_secondary_education:
        secondary_education_exam = mdl.secondary_education_exam.find_by_type(a_secondary_education, 'ADMISSION')
        if secondary_education_exam:
            if secondary_education_exam.admission_exam_type:
                offer_admission_exam_type = mdl.offer_admission_exam_type.find_by_offer_year(an_application.offer_year)
                if offer_admission_exam_type:
                    if secondary_education_exam.admission_exam_type == offer_admission_exam_type.admission_exam_type:
                        return _(SPECIAL_EXAM_ADMISSION_NEEDED_TXT)
                else:
                    return _(EXAM_ADMISSION_DOC_NEEDED_TXT)
    return ""


def get_message_secondary_diploma_document(an_applicant):
    a_secondary_education = mdl.secondary_education.search(an_applicant, True)
    if a_secondary_education:
        return "{0} {1}".format(_(SECONDARY_DIPLOMA_NEEDED_TXT),
                                get_academic_year(a_secondary_education[0].academic_year))
    else:
        return ""


def get_message_capaes_document(an_institutional_grade_type):
    if is_capaes(an_institutional_grade_type):
        return _(CAPAES_DOC_NEEDED_TXT)
    return ""


def get_message_capaes_identification_document(an_institutional_grade_type):
    if is_capaes(an_institutional_grade_type):
        return _(CAPAES_IDENTIFICATION_DOC_NEEDED_TXT)
    return ""


def get_opes_url(an_offer_acronym):
    if an_offer_acronym and (an_offer_acronym.upper()).startswith('OPES'):
        return _(OPES_URL_TXT)
    return ""


def get_fopa_url(an_offer_acronym):
    if an_offer_acronym and (an_offer_acronym.upper()).startswith('FOPA'):
        return _(FOPA_URL_TXT)
    return ""


def is_capaes(an_institutional_grade_type):
    if an_institutional_grade_type == enum_institutional_grade_type.CAPAES:
        return True
    return False


def get_capaes_dates_paragraph(an_institutional_grade_type, academic_year):
    capaes_paragraph_parts = []
    if is_capaes(an_institutional_grade_type):
        capaes_paragraph_parts.append(capaes_dates_paragraph_line1)
        capaes_paragraph_parts.append(capaes_dates_paragraph_line2(academic_year))
        capaes_paragraph_parts.append(capaes_dates_paragraph_line3(academic_year))
    return capaes_paragraph_parts


def capaes_dates_paragraph_line1():
    return _('capaes_limit_date_part1')


def capaes_dates_paragraph_line2(academic_year):
    return "{0}{1}{2}{3}{4}".format(_('capaes_limit_date_part2_start'),
                                    format_academic_year(academic_year),
                                    _('capaes_limit_date_part2_middle'),
                                    format_academic_year(academic_year),
                                    _('capaes_limit_date_part2_end'))


def capaes_dates_paragraph_line3(academic_year):
    return "{0}{1}{2}".format(_('capaes_limit_date_part3_start'),
                              format_academic_year(academic_year),
                              _('capaes_limit_date_part3_end'))


def format_academic_year(academic_year):
    if academic_year is None:
        return ""
    return academic_year


# def text_display(an_applicant, an_application):
#     template_reference = get_model_message(an_application.application_type)
#     message_content = {'html_template_ref': '{0}_html'.format(template_reference),
#                        'txt_template_ref': '{0}_txt'.format(template_reference)}
#
#
#     if an_application.application_type=='ADMISSION':
#         data = message_template_admission_variables(an_applicant, an_application)
#     else:
#         data = message_template_inscription_variables(an_applicant, an_application)
#
#     message_content['template_base_data'] = data
#
#     return send_message.get_body_content(message_content)