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

import admission.tests.data_for_tests as data_model
from admission.views import submission
from admission.models.enums import application_type
from admission import models as mdl
from reference import models as mdl_ref
from base import models as mdl_base
from reference.enums import institutional_grade_type as enum_institutional_grade_type

BASIC_URL_PART1 = 'http://www.uclouvain.be/'
BASIC_URL_PART2 = '357540.html'

LAST_NAME = 'jacob'
FIRST_NAME = 'toto'

now = datetime.datetime.now()


class SubmissionTest(TestCase):

    def setUp(self):
        a_user = User.objects.create_user(
            username='jacob',
            last_name=LAST_NAME,
            first_name=FIRST_NAME,
            email='jacob@localhost',
            password='top_secret')
        self.applicant = data_model.create_applicant_by_user(a_user)
        self.application = data_model.create_application(self.applicant)
        activate('en')
        self.basic_url = "{0}{1}".format(BASIC_URL_PART1, BASIC_URL_PART2)
        self.english_url = "{0}{1}{2}".format(BASIC_URL_PART1, submission.ENGLISH_URL_PREFIX, BASIC_URL_PART2)
        self.grade_type = mdl_ref.grade_type.GradeType(
            name='Master complémentaire',
            institutional_grade_type=enum_institutional_grade_type.ADVANCED_MASTER,
            url_info=self.basic_url)
        academic_yr = mdl_base.academic_year.AcademicYear(
            year=(now.year - 1),
            start_date=datetime.datetime(now.year - 1, now.month, 15),
            end_date=datetime.datetime(now.year, now.month, 28))
        academic_yr.save()
        academic_yr = mdl_base.academic_year.AcademicYear(
            year=now.year,
            start_date=datetime.datetime(now.year, now.month, 1),
            end_date=datetime.datetime(now.year + 1, now.month, 28))
        academic_yr.save()

    def test_get_title_mister(self):
        title = submission.get_title(mdl.applicant.Applicant(gender=mdl.applicant.MALE))
        self.assertTrue((title == 'Mister'))

    def test_get_title_madam(self):
        title = submission.get_title(mdl.applicant.Applicant(gender=mdl.applicant.FEMALE,
                                                             civil_status=mdl.applicant.MARRIED))
        self.assertTrue((title == 'Madam'))

    def test_get_title_miss(self):
        title = submission.get_title(mdl.applicant.Applicant(gender=mdl.applicant.FEMALE,
                                                             civil_status=mdl.applicant.COHABITANT))
        self.assertTrue((title == 'Miss'))

    def test_get_title_no_gender(self):
        title = submission.get_title(mdl.applicant.Applicant(gender=None))
        self.assertTrue((title == 'Madam, Mister'))

    def test_get_submission_docs_url_fr_en(self):
        self.assertTrue((submission.get_submission_docs_url(self.grade_type)) == [self.basic_url, self.english_url])

    def test_get_submission_docs_url_missing(self):
        grade_type = mdl_ref.grade_type.GradeType(
            name='Master complémentaire',
            institutional_grade_type=enum_institutional_grade_type.ADVANCED_MASTER,
            url_info=None)
        self.assertIsNone((submission.get_submission_docs_url(grade_type)))

    def test_get_submission_docs_wrong_url(self):
        wrong_url = "google.zzz"
        grade_type = mdl_ref.grade_type.GradeType(
            name='Master complémentaire',
            institutional_grade_type=enum_institutional_grade_type.ADVANCED_MASTER,
            url_info=wrong_url)
        self.assertIsNone((submission.get_submission_docs_url(grade_type)))

    def test_find_model_admission(self):
        self.assertTrue(submission.find_model_reference(application_type.ADMISSION) == submission.MODELE_ADMISSION)

    def test_find_model_inscription(self):
        self.assertTrue(submission.find_model_reference(application_type.INSCRIPTION) == submission.MODELE_INSCRIPTON)

    def test_find_model_unkknown_application_type(self):
        self.assertIsNone(submission.find_model_reference("wrong_application_type"))

    def test_find_model_none_application_type(self):
        self.assertIsNone(submission.find_model_reference(None))

    def test_get_model_message_admission(self):
        data_model.create_message_template(submission.MODELE_ADMISSION,
                                           'a_subject',
                                           'test',
                                           'PLAIN',
                                           'fr-be')
        self.assertIsNotNone(submission.get_model_message(application_type.ADMISSION))

    def test_get_submission_docs_url_fr(self):
        self.assertTrue((submission.get_submission_docs_url_fr(self.grade_type)) == self.basic_url)

    def test_get_submission_docs_url_en(self):
        self.assertTrue((submission.get_submission_docs_url_en(self.grade_type)) == self.english_url)

    def test_get_academic_year(self):
        year_plus_one = self.application.offer_year.academic_year.year+1
        expected_result = "{0}-{1}".format(str(self.application.offer_year.academic_year.year), str(year_plus_one))
        self.assertTrue(
            (submission.get_academic_year(self.application.offer_year.academic_year.year)) == expected_result)

    def test_get_subject_to_quota_txt_present(self):
        self.assertIsNotNone(submission.get_subject_to_quota_txt_part(True, 1))
        self.assertIsNotNone(submission.get_subject_to_quota_txt_part(True, 2))
        self.assertIsNotNone(submission.get_subject_to_quota_txt_part(True, 3))

    def test_get_subject_to_quota_txt_empty(self):
        self.assertTrue(submission.get_subject_to_quota_txt_part(None, 1) == "")

    def test_get_variables_for_message_template(self):
        self.applicant.gender = mdl.applicant.MALE
        self.application.offer_year.grade_type = self.grade_type
        self.application.offer_year.subject_to_quota = True

        year_plus_one = self.application.offer_year.academic_year.year+1
        academic_year = "{0}-{1}".format(str(self.application.offer_year.academic_year.year), str(year_plus_one))
        data = {'last_name': LAST_NAME,
                'first_name': FIRST_NAME,
                'reference': '',
                'title': 'Mister',
                'url_fr': self.basic_url,
                'url_en': self.english_url,
                'academic_year': academic_year,
                'subject_to_quota_txt1': 'subject_to_quota_txt_part1',
                'subject_to_quota_txt2': 'subject_to_quota_txt_part2',
                'subject_to_quota_txt3': 'subject_to_quota_txt_part3',
                'responsible': '',
                'organization_name': '',
                'organization_street': '',
                'organization_city': '',
                'organization_country': '',
                'closing_date': ''}

        self.assertTrue(submission.message_template_admission_variables(self.applicant, self.application) == data)

    def test_onem_document_needed(self):
        data_model.create_curriculum(self.applicant, 'UNEMPLOYMENT')
        self.assertTrue(submission.get_message_document(self.applicant, 'UNEMPLOYMENT') != "")

    def test_onem_document_unneeded(self):
        self.assertTrue(submission.get_message_document(self.applicant, 'UNEMPLOYMENT') == "")

    def test_debts_document_needed(self):
        country_belgium = mdl_ref.country.Country(iso_code='BE')
        country_belgium.save()
        national_institution = data_model.create_education_institution('national_institution', country_belgium)
        curriculum = data_model.create_curriculum(self.applicant, None)
        curriculum.academic_year = now.year-2
        curriculum.path_type = 'LOCAL_UNIVERSITY'
        curriculum.national_education = 'FRENCH'
        curriculum.national_institution = national_institution
        curriculum.save()

        self.assertTrue(submission.get_debts_document(self.application) != "")

    def test_debts_document_unneeded(self):
        self.assertTrue(submission.get_debts_document(self.application) == "")

    def test_other_activity_type_document_needed(self):
        curriculum = data_model.create_curriculum(self.applicant, 'OTHER')
        curriculum.academic_year = now.year - 2
        curriculum.save()
        curriculum = data_model.create_curriculum(self.applicant, 'OTHER')
        curriculum.academic_year = now.year - 3
        curriculum.save()
        self.assertTrue(submission.get_other_activity_type_document(self.applicant) != "")

    def test_other_activity_type_document_unneeded(self):
        self.assertTrue(submission.get_other_activity_type_document(self.applicant) == "")

    def test_studies_document_needed(self):
        curriculum = data_model.create_curriculum(self.applicant, None)
        curriculum.path_type = 'LOCAL_UNIVERSITY'
        curriculum.save()
        self.assertTrue(submission.get_message_studies_document(self.applicant) != "")

    def test_studies_document_unneeded(self):
        self.assertTrue(submission.get_message_studies_document(self.applicant) == "")

    def test_exam_admission_document_needed_for_engineer(self):
        secondary_education = data_model.create_secondary_education_with_applicant(self.applicant)
        admission_exam_type = data_model.create_admission_exam_type()
        secondary_education_exam = data_model.create_secondary_education_exam(secondary_education, 'ADMISSION')
        secondary_education_exam.admission_exam_type = admission_exam_type
        secondary_education_exam.save()
        offer_admission_exam_type = data_model.create_offer_admission_exam_type(self.application.offer_year)
        offer_admission_exam_type.admission_exam_type = admission_exam_type
        offer_admission_exam_type.save()

        self.assertTrue(
            submission.get_message_exam_admission_document(self.applicant, self.application) == "special_exam_admission_doc_needed")

    def test_exam_admission_document_needed(self):
        secondary_education = data_model.create_secondary_education_with_applicant(self.applicant)
        admission_exam_type = data_model.create_admission_exam_type()
        secondary_education_exam = data_model.create_secondary_education_exam(secondary_education, 'ADMISSION')
        secondary_education_exam.admission_exam_type = admission_exam_type
        secondary_education_exam.save()
        self.assertTrue(
            submission.get_message_exam_admission_document(self.applicant, self.application) == "exam_admission_doc_needed")

    def test_exam_admission_document_unneeded(self):
        self.assertTrue(submission.get_message_exam_admission_document(self.applicant, self.application) == "")

    def test_secondary_diploma_document_needed(self):
        secondary_education = data_model.create_secondary_education_with_applicant(self.applicant)
        secondary_education.diploma = True
        secondary_education.save()
        self.assertTrue(submission.get_message_secondary_diploma_document(self.applicant) != "")

    def test_secondary_diploma_document_unneeded(self):
        secondary_education = data_model.create_secondary_education_with_applicant(self.applicant)
        secondary_education.diploma = False
        secondary_education.save()
        self.assertTrue(submission.get_message_secondary_diploma_document(self.applicant) == "")

    def test_capaes_document_needed(self):
        grade_type = mdl_ref.grade_type.GradeType(institutional_grade_type=enum_institutional_grade_type.CAPAES)
        grade_type.save()
        self.application.offer_year.grade_type = grade_type
        self.application.offer_year.grade_type.save()
        self.assertTrue(submission.get_message_capaes_document(self.application) != "")

    def test_capaes_document_unneeded(self):
        grade_type = mdl_ref.grade_type.GradeType(institutional_grade_type=enum_institutional_grade_type.BACHELOR)
        grade_type.save()
        self.application.offer_year.grade_type = grade_type
        self.application.offer_year.grade_type.save()
        self.assertTrue(submission.get_message_capaes_document(self.application) == "")

    def test_send_submission_email_for_admission(self):

        self.application.application_type = application_type.ADMISSION

        try:
            submission.send_soumission_email()
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_send_soumission_email_for_admission"))
