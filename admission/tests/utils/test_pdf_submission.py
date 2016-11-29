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
import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from admission.models import curriculum

import admission.tests.data_for_tests as data_model
from admission.utils import pdf_submission
from admission.models.enums import application_type
from admission import models as mdl
from reference import models as mdl_ref
from reference.enums import institutional_grade_type as enum_institutional_grade_type
import datetime
from admission.models.enums import education, professional_activity


LAST_NAME = 'jacob'
FIRST_NAME = 'toto'
MIDDLE_NAME = 'Jules'
BIRTH_PLACE = 'NAMUR'
BELGIUM = 'BELGIUM'
MARRIED = 'MARRIED'
SPOUSE_NAME = 'Maria Theresa'
CHILDREN = 3
DATE_USED = datetime.datetime.now()

MOBILE = '+32 498 51 74 98'
ADDITIONAL_EMAIL = 'delphine.schreuder@localhost.com'

now = datetime.datetime.now()

ADMISSION_EXAM_TYPE = 'ADMISSION'
LANGUAGE_EXAM_TYPE = 'LANGUAGE'

LEGAL_ADDRESS = 'LEGAL'
CONTACT_ADDRESS = 'CONTACT'


class PdfSubmissionTest(TestCase):

    def setUp(self):
        self.country_belgium = self.create_belgium_country()
        self.applicant = self.create_default_applicant()
        self.application = data_model.create_application(self.applicant)
        self.secondary_education = data_model.create_secondary_education_with_applicant(self.applicant)

        activate('en')

        self.curriculum_other = data_model.create_curriculum_from_data({'applicant':     self.applicant,
                                                                        'path_type':     'ANOTHER_ACTIVITY',
                                                                        'activity_type': 'OTHER',
                                                                        'academic_year': now.year-1})
        grade_type = data_model.create_grade_type('Bachelier', 'BACHELOR')

        education_institution = data_model.create_education_institution('Saint-Berthuin', self.country_belgium)

        self.curriculum_university = data_model.create_curriculum_from_data({
            'applicant':       self.applicant,
            'path_type':            'LOCAL_UNIVERSITY',
            'academic_year':        now.year-2,
            'grade_type':           grade_type,
            'national_institution': education_institution,
            'result':               'SUCCEED',
            'diploma':              True,
            'credits_enrolled':     25})
        self.curriculum_foreign_university = data_model.create_curriculum_from_data({
            'applicant':            self.applicant,
            'path_type':            'FOREIGN_UNIVERSITY',
            'academic_year':        now.year-3,
            'grade_type':           grade_type,
            'national_institution': None,
            'result':               'SUCCEED',
            'diploma':              True})

    def create_belgium_country(self):
        country_belgium = mdl_ref.country.Country(iso_code='BE', name=BELGIUM)
        country_belgium.save()
        return country_belgium

    def create_default_applicant(self):
        a_user = User.objects.create_user(
            username='jacob',
            last_name=LAST_NAME,
            first_name=FIRST_NAME,
            email='jacob@localhost',
            password='top_secret')
        applicant = data_model.create_applicant_by_user(a_user)
        applicant.middle_name = MIDDLE_NAME
        applicant.birth_date = DATE_USED
        applicant.birth_place = BIRTH_PLACE
        applicant.birth_country = self.country_belgium
        applicant.civil_status = MARRIED
        applicant.spouse_name = SPOUSE_NAME
        applicant.number_children = CHILDREN
        applicant.phone_mobile = MOBILE
        applicant.additional_email = ADDITIONAL_EMAIL

        return applicant

    def test_get_existing_secondary_education(self):
        self.assertTrue(pdf_submission.get_secondary_education(self.applicant) == self.secondary_education)

    def test_get_existing_secondary_education_exam_admission(self):
        self.get_secondary_education_exam(self.secondary_education, ADMISSION_EXAM_TYPE)

    def get_secondary_education_exam(self, secondary_education, a_secondary_education_exam_type):
        secondary_education_admission_exam = data_model.create_secondary_education_exam(secondary_education,
                                                                                        a_secondary_education_exam_type)
        self.assertTrue(pdf_submission.get_secondary_exam(secondary_education,
                                                          a_secondary_education_exam_type) == secondary_education_admission_exam)

    def test_get_no_secondary_education(self):
        self.assertIsNone(pdf_submission.get_secondary_exam(self.secondary_education, ADMISSION_EXAM_TYPE))

    def test_get_existing_secondary_education_exam_language(self):
        self.get_secondary_education_exam(self.secondary_education, LANGUAGE_EXAM_TYPE)

    def test_get_no_secondary_education_exam_language(self):
        self.assertIsNone(pdf_submission.get_secondary_exam(self.secondary_education, LANGUAGE_EXAM_TYPE))

    def test_get_curriculum_studies_list(self):
        curriculum_list = [self.curriculum_university,
                           self.curriculum_foreign_university]
        self.assertTrue(list(pdf_submission.get_curriculum_list(self.applicant, ['LOCAL_UNIVERSITY',
                                                                                 'FOREIGN_UNIVERSITY',
                                                                                 'LOCAL_HIGH_EDUCATION',
                                                                                 'FOREIGN_HIGH_EDUCATION'])) == curriculum_list)

    def test_get_curriculum_other_list(self):
        curriculum_list = [self.curriculum_other]
        self.assertTrue(list(pdf_submission.get_curriculum_list(self.applicant,
                                                                ['ANOTHER_ACTIVITY'])) == curriculum_list)

    def test_get_sociological_survey(self):
        profession = data_model.create_profession('Boucher', True)
        sociological_survey = data_model.create_sociological_survey({'applicant': self.applicant,
                                                                     'number_brothers_sisters': 1,
                                                                     'father_is_deceased': True,
                                                                     'father_education': education.PRIMARY,
                                                                     'father_profession': None,
                                                                     'mother_is_deceased': False,
                                                                     'mother_education': education.SECONDARY_INFERIOR,
                                                                     'mother_profession': None,
                                                                     'student_professional_activity': professional_activity.PART_TIME,
                                                                     'student_profession': None,
                                                                     'conjoint_professional_activity': professional_activity.NO_PROFESSION,
                                                                     'conjoint_profession': None,
                                                                     'paternal_grandfather_profession': profession,
                                                                     'maternal_grandfather_profession': profession})

        self.assertTrue(pdf_submission.get_sociological_survey(self.applicant) == sociological_survey)

    def test_sociological_survey_not_existing(self):
        self.assertIsNone(pdf_submission.get_sociological_survey(self.applicant))

    def test_get_person_contact_address(self):
        person_address_contact = self.create_person_address(CONTACT_ADDRESS)
        self.assertTrue(pdf_submission.get_person_address(self.applicant, CONTACT_ADDRESS) == person_address_contact)

    def test_get_person_legal_address(self):
        person_address_contact = self.create_person_address(LEGAL_ADDRESS)
        self.assertTrue(pdf_submission.get_person_address(self.applicant, LEGAL_ADDRESS) == person_address_contact)

    def create_person_address(self, a_type):
        return data_model.create_person_address({'applicant': self.applicant,
                                                 'type': a_type,
                                                 'street': 'street',
                                                 'number': 25,
                                                 'complement': None,
                                                 'postal_code': '5020',
                                                 'city': 'Malonne',
                                                 'country': self.country_belgium})




