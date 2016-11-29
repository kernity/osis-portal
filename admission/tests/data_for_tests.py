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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.models import User
from admission import models as mdl
from base import models as mdl_base
from reference import models as mdl_reference
from osis_common import models as mdl_osis_common
from reference.enums import assimilation_criteria as assimilation_criteria_enum
from django.utils import timezone
import datetime


def create_user():
    a_user = User.objects.create_user('testo', password='testopw')
    a_user.save()
    return a_user


def get_or_create_user():
    a_user, created = User.objects.get_or_create(username='testo', password='testopw')
    if created:
        a_user.save()
    return a_user


def get_or_create_applicant():
    an_applicant = mdl.applicant.find_by_user(user=get_or_create_user())
    if not an_applicant:
        an_applicant = mdl.applicant.Applicant(user=get_or_create_user())
        an_applicant.save()
    return an_applicant


def get_or_create_profession(name, adhoc):
    a_profession = mdl.profession.find_by_name(name)
    if not a_profession:
        a_profession = mdl.profession.Profession(name=name, adhoc=adhoc)
        a_profession.save()
    return a_profession


def create_applicant_by_user(user):
    an_applicant = mdl.applicant.Applicant(user=user)
    an_applicant.save()
    return an_applicant


def create_applicant():
    an_applicant = mdl.applicant.Applicant(user=create_user())
    an_applicant.save()
    return an_applicant


def create_secondary_education():
    a_secondary_education = mdl.secondary_education.SecondaryEducation(person=create_applicant())
    a_secondary_education.save()
    return a_secondary_education


def create_secondary_education_exam(secondary_education, a_type):
        an_admission_exam = mdl.secondary_education_exam.SecondaryEducationExam(
            secondary_education=secondary_education,
            type=a_type)
        an_admission_exam.save()
        return an_admission_exam


def create_secondary_education_with_exams():
    secondary_education = create_secondary_education()
    create_secondary_education_exam(secondary_education, 'ADMISSION')
    create_secondary_education_exam(secondary_education, 'PROFESSIONAL')
    create_secondary_education_exam(secondary_education, 'LANGUAGE')
    return secondary_education


def create_application(an_applicant):
    an_application = mdl.application.Application(applicant=an_applicant,
                                                 offer_year=create_offer_year(),
                                                 application_type='ADMISSION')
    an_application.save()
    return an_application


def create_offer_year():
    an_offer_year = mdl_base.offer_year.OfferYear()
    an_offer_year.academic_year = create_academic_year()
    an_offer_year.acronym = "VETE11BA"
    an_offer_year.title = "Première année de bachelier en médecine vétérinaire"
    an_offer_year.save()
    return an_offer_year


def create_academic_year():
    an_academic_year = mdl_base.academic_year.AcademicYear()
    an_academic_year.year = 2016
    an_academic_year.save()
    return an_academic_year


def create_grade_type(a_name, an_institutional_grade_type):
    a_grade_type = mdl_reference.grade_type.GradeType(name=a_name, institutional_grade_type=an_institutional_grade_type)
    a_grade_type.save()
    return a_grade_type


def create_document_file(update_by, description=None):
    a_document_file = mdl_osis_common.document_file.DocumentFile(description=description)
    a_document_file.file_name = "test.jpg"
    a_document_file.storage_duration = 1
    a_document_file.update_by = update_by
    a_document_file.save()
    return a_document_file


def create_application_document_file(an_application, update_by, description=None):
    a_document_file = create_document_file(update_by, description)
    an_application_document_file = mdl.application_document_file.ApplicationDocumentFile()
    an_application_document_file.application = an_application
    an_application_document_file.document_file = a_document_file
    an_application_document_file.save()
    return an_application_document_file


def create_profession(a_name, an_adhoc):
    return mdl.profession.Profession(name=a_name, adhoc=an_adhoc)


def create_applicant_assimilation_criteria(an_applicant):
    return mdl.applicant_assimilation_criteria.ApplicantAssimilationCriteria(
        applicant=an_applicant,
        criteria=assimilation_criteria_enum.ASSIMILATION_CRITERIA_CHOICES[0][0],
        additional_criteria=None,
        selected=False)


def create_applicant_document_file(an_applicant, description):
    a_document_file = create_document_file(an_applicant.user.username, description)
    an_applicant_document_file = mdl.applicant_document_file.ApplicantDocumentFile()
    an_applicant_document_file.applicant = an_applicant
    an_applicant_document_file.document_file = a_document_file
    an_applicant_document_file.save()
    return an_applicant_document_file


def create_message_template(a_reference, a_subject, a_template, a_format, a_language):
    message_template = mdl_osis_common.message_template.MessageTemplate(reference=a_reference,
                                                                        subject=a_subject,
                                                                        template=a_template,
                                                                        format=a_format,
                                                                        language=a_language)

    message_template.save()
    return message_template


def create_curriculum(an_applicant, an_activity_type, year):
    curriculum = mdl.curriculum.Curriculum(person=an_applicant,
                                           activity_type=an_activity_type)
    curriculum.academic_year = year
    curriculum.save()
    return curriculum


def create_current_academic_year():
    now = datetime.datetime.now()
    an_academic_year = mdl_base.academic_year.AcademicYear()
    an_academic_year.year = now.year
    an_academic_year.start_date = now - datetime.timedelta(2)
    an_academic_year.end_date = now + datetime.timedelta(2)
    an_academic_year.save()
    return an_academic_year


def create_education_institution(a_name, a_country):
    education_institution = mdl_reference.education_institution.EducationInstitution(name=a_name, country=a_country)
    education_institution.save()
    return education_institution


def create_admission_exam_type():
    admission_exam_type = mdl.admission_exam_type.AdmissionExamType(name='Admission exam type')
    admission_exam_type.save()
    return admission_exam_type


def create_offer_admission_exam_type(an_offer_year):
    admission_exam_type = create_admission_exam_type()
    offer_admission_exam_type = mdl.offer_admission_exam_type.OfferAdmissionExamType(
        offer_year=an_offer_year,
        admission_exam_type=admission_exam_type)
    offer_admission_exam_type.save()
    return offer_admission_exam_type


def create_secondary_education_with_applicant(an_applicant):
    a_secondary_education = mdl.secondary_education.SecondaryEducation(person=an_applicant)
    a_secondary_education.save()
    return a_secondary_education


def create_curriculum_from_data(data):
    curriculum = mdl.curriculum.Curriculum()
    if 'applicant' in data:
        curriculum.person = data['applicant']
    if 'academic_year' in data:
        curriculum.academic_year = data['academic_year']
    if 'path_type' in data:
        curriculum.path_type = data['path_type']
    if 'national_education' in data:
        curriculum.national_education = data['national_education']
    if 'grade_type' in data:
        curriculum.grade_type = data['grade_type']
    if 'grade_type_no_university' in data:
        curriculum.grade_type_no_university = data['grade_type_no_university']
    if 'domain' in data:
        curriculum.domain = data['domain']
    if 'sub_domain' in data:
        curriculum.sub_domain = data['sub_domain']
    if 'result' in data:
        curriculum.result = data['result']
    if 'credits_enrolled' in data:
        curriculum.credits_enrolled = data['credits_enrolled']
    if 'credits_obtained' in data:
        curriculum.credits_obtained = data['credits_obtained']
    if 'diploma' in data:
        curriculum.diploma = data['diploma']
    if 'activity_type' in data:
        curriculum.activity_type = data['activity_type']
    curriculum.save()
    return curriculum


def create_sociological_survey(data):
    sociological_survey = mdl.sociological_survey.SociologicalSurvey()
    if 'applicant' in data:
        sociological_survey.applicant = data['applicant']
    if 'number_brothers_sisters' in data:
        sociological_survey.number_brothers_sisters = data['number_brothers_sisters']
    if 'father_is_deceased' in data:
        sociological_survey.father_is_deceased = data['father_is_deceased']
    if 'father_education' in data:
        sociological_survey.father_education = data['father_education']
    if 'father_profession' in data:
        sociological_survey.father_profession = data['father_profession']
    if 'mother_is_deceased' in data:
        sociological_survey.mother_is_deceased = data['mother_is_deceased']
    if 'mother_education' in data:
        sociological_survey.mother_education = data['mother_education']
    if 'mother_profession' in data:
        sociological_survey.mother_profession = data['mother_profession']
    if 'student_professional_activity' in data:
        sociological_survey.student_professional_activity = data['student_professional_activity']
    if 'student_profession' in data:
        sociological_survey.student_profession = data['student_profession']
    if 'conjoint_professional_activity' in data:
        sociological_survey.conjoint_professional_activity = data['conjoint_professional_activity']
    if 'conjoint_profession' in data:
        sociological_survey.conjoint_profession = data['conjoint_profession']
    if 'paternal_grandfather_profession' in data:
        sociological_survey.paternal_grandfather_profession = data['paternal_grandfather_profession']
    if 'maternal_grandfather_profession' in data:
        sociological_survey.maternal_grandfather_profession = data['maternal_grandfather_profession']
    sociological_survey.save()
    return sociological_survey


def create_person_address(data):
    person_address = mdl.person_address.PersonAddress()
    if 'applicant' in data:
        person_address.person = data['applicant']
    if 'type' in data:
        person_address.type = data['type']
    if 'street' in data:
        person_address.street = data['street']
    if 'number' in data:
        person_address.number = data['number']
    if 'complement' in data:
        person_address.complement = data['complement']
    if 'postal_code' in data:
        person_address.postal_code = data['postal_code']
    if 'city' in data:
        person_address.city = data['city']
    if 'country' in data:
        person_address.country = data['country']
    person_address.save()
    return person_address
