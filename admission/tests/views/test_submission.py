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

import admission.tests.data_for_tests as data_model
from admission.views import submission
from admission.models.enums import application_type
from admission import models as mdl
from reference import models as mdl_ref
from base import models as mdl_base
from reference.enums import institutional_grade_type as enum_institutional_grade_type

NUMBER_OF_LINES_IN_CAPAES_PARAGRAPH = 3

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
        self.assertTrue(submission.find_model_reference(application_type.ADMISSION) == submission.MODEL_ADMISSION)

    def test_find_model_inscription(self):
        self.assertTrue(submission.find_model_reference(application_type.INSCRIPTION) == submission.MODEL_INSCRIPTON)

    def test_find_model_unkknown_application_type(self):
        self.assertIsNone(submission.find_model_reference("wrong_application_type"))

    def test_find_model_none_application_type(self):
        self.assertIsNone(submission.find_model_reference(None))

    def test_get_model_message_admission(self):
        data_model.create_message_template(submission.MODEL_ADMISSION,
                                           'a_subject',
                                           'test {{title}}',
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
        data = {submission.VARIABLE_LAST_NAME: LAST_NAME,
                submission.VARIABLE_FIRST_NAME: FIRST_NAME,
                submission.VARIABLE_REFERENCE: '',
                submission.VARIABLE_TITLE: 'Mister',
                submission.VARIABLE_ADMISSION_URL_FR: self.basic_url,
                submission.VARIABLE_ADMISSION_URL_EN: self.english_url,
                submission.VARIABLE_ADMISSION_ACADEMIC_YEAR: academic_year,
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_1: 'subject_to_quota_txt_part1',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_2: 'subject_to_quota_txt_part2',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_3: 'subject_to_quota_txt_part3',
                submission.VARIABLE_RESPONSIBLE: '',
                submission.VARIABLE_ORGANIZATION_NAME: '',
                submission.VARIABLE_ORGANIZATION_STREET: '',
                submission.VARIABLE_ORGANIZATION_CITY: '',
                submission.VARIABLE_ORGANIZATION_COUNTRY: '',
                submission.VARIABLE_CLOSING_DATE: ''}

        self.assertTrue(submission.message_template_admission_variables(self.applicant, self.application) == data)

    def test_onem_document_needed(self):
        data_model.create_curriculum(self.applicant, 'UNEMPLOYMENT')
        self.assertTrue(submission.get_message_document(self.applicant, 'UNEMPLOYMENT') != "")

    def test_onem_document_unneeded(self):
        self.assertTrue(submission.get_message_document(self.applicant, 'UNEMPLOYMENT') == "")

    def test_debts_document_needed(self):
        self.create_data_debts_doc_needed()
        self.assertTrue(submission.get_debts_document(self.application) != "")

    def create_data_debts_doc_needed(self):
        country_belgium = mdl_ref.country.Country(iso_code='BE')
        country_belgium.save()
        national_institution = data_model.create_education_institution('national_institution', country_belgium)
        curriculum = data_model.create_curriculum(self.applicant, None)
        curriculum.academic_year = now.year - 2
        curriculum.path_type = 'LOCAL_UNIVERSITY'
        curriculum.national_education = 'FRENCH'
        curriculum.national_institution = national_institution
        curriculum.save()

    def test_debts_document_unneeded(self):
        self.assertTrue(submission.get_debts_document(self.application) == "")

    def test_other_activity_type_document_needed(self):
        an_activity_type = 'OTHER'
        curriculum = data_model.create_curriculum(self.applicant, an_activity_type)
        curriculum.academic_year = now.year - 2
        curriculum.save()
        curriculum = data_model.create_curriculum(self.applicant, an_activity_type)
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
            submission.
            get_message_exam_admission_document(self.applicant, self.application) ==
            _(submission.SPECIAL_EXAM_ADMISSION_NEEDED_TXT))

    def test_exam_admission_document_needed(self):
        self.create_admission_exam_data()
        self.assertTrue(
            submission.get_message_exam_admission_document(self.applicant, self.application) ==
            _(submission.EXAM_ADMISSION_DOC_NEEDED_TXT))

    def create_admission_exam_data(self):
        secondary_education = data_model.create_secondary_education_with_applicant(self.applicant)
        secondary_education.diploma = True
        secondary_education.save()
        admission_exam_type = data_model.create_admission_exam_type()
        secondary_education_exam = data_model. \
            create_secondary_education_exam(secondary_education,
                                            'ADMISSION')
        secondary_education_exam.admission_exam_type = admission_exam_type
        secondary_education_exam.save()

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
        self.assertTrue(submission.get_message_capaes_document(enum_institutional_grade_type.CAPAES) == _(submission.CAPAES_DOC_NEEDED_TXT))

    def test_capaes_document_unneeded(self):
        self.assertTrue(submission.get_message_capaes_document(enum_institutional_grade_type.BACHELOR) == "")

    def test_capaes_identification_document_needed(self):
        self.assertTrue(submission.get_message_capaes_identification_document(enum_institutional_grade_type.CAPAES) == _(submission.CAPAES_IDENTIFICATION_DOC_NEEDED_TXT))

    def test_capaes_identification_document_unneeded(self):
        self.assertTrue(submission.get_message_capaes_identification_document(enum_institutional_grade_type.BACHELOR) == "")

    def test_opes_url_needed(self):
        self.assertTrue(submission.get_opes_url("OPES2MS/ES") == _(submission.OPES_URL_TXT))

    def test_opes_url_unneeded(self):
        self.assertTrue(submission.get_opes_url("COMU11BA") == "")

    def test_opes_url_needed_with_empty_acronym(self):
        self.assertTrue(submission.get_opes_url("") == "")

    def test_opes_url_needed_with_null_acronym(self):
        self.assertTrue(submission.get_opes_url(None) == "")

    def test_fopa_url_needed(self):
        self.assertTrue(submission.get_fopa_url("FOPA2MG/G") == _(submission.FOPA_URL_TXT))

    def test_fopa_url_unneeded(self):
        self.assertTrue(submission.get_fopa_url("COMU11BA") == "")

    def test_capaes_dates_number_information_correct(self):
        dict_paragraph = submission.get_capaes_dates_paragraph(enum_institutional_grade_type.CAPAES, 2016)
        self.assertTrue(len(dict_paragraph) == NUMBER_OF_LINES_IN_CAPAES_PARAGRAPH)

    def test_capaes_dates_number_information_ZERO(self):
        dict_paragraph = submission.get_capaes_dates_paragraph(enum_institutional_grade_type.BACHELOR, 2016)
        self.assertTrue(len(dict_paragraph) == 0)

    def test_get_variables_for_message_template_for_inscription_capaes(self):
        self.applicant.gender = mdl.applicant.MALE

        application_capaes = self.create_application_by_institutional_grade_type(enum_institutional_grade_type.CAPAES)
        self.create_curriculum_list('OTHER', 2, now.year)
        year_plus_one = application_capaes.offer_year.academic_year.year+1
        academic_year = "{0}-{1}".format(str(application_capaes.offer_year.academic_year.year), str(year_plus_one))
        data_model.create_curriculum(self.applicant, 'UNEMPLOYMENT')

        self.create_admission_exam_data()
        self.create_data_debts_doc_needed()
        data = {submission.VARIABLE_LAST_NAME: LAST_NAME,
                submission.VARIABLE_FIRST_NAME: FIRST_NAME,
                submission.VARIABLE_REFERENCE: '',
                submission.VARIABLE_ENROLLMENT_OFFER_ACRONYM: application_capaes.offer_year.acronym,
                submission.VARIABLE_TITLE: 'Mister',
                submission.VARIABLE_ENROLLMENT_YEAR: application_capaes.offer_year.academic_year.year,
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_1: 'subject_to_quota_txt_part1',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_2: 'subject_to_quota_txt_part2',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_3: 'subject_to_quota_txt_part3',
                submission.VARIABLE_RESPONSIBLE: '',
                submission.VARIABLE_ORGANIZATION_NAME: '',
                submission.VARIABLE_ORGANIZATION_STREET: '',
                submission.VARIABLE_ORGANIZATION_CITY: '',
                submission.VARIABLE_ORGANIZATION_COUNTRY: '',
                submission.VARIABLE_CLOSING_DATE: '',
                submission.VARIABLE_ENROLLMENT_UNEMPLOYMENT_DOC: _(submission.UNEMPLOYMENT_DOC_NEEDED_TXT),
                submission.VARIABLE_ENROLLMENT_DEBTS_DOC: _(submission.DEBTS_DOC_NEEDED_TXT),
                submission.VARIABLE_ENROLLMENT_OTHER_ACTIVITIES_DOC: " {0} {1} {2} {3}".format(_(submission.OTHER_DOC_NEEDED_TXT),
                            submission.get_academic_year(now.year-3),
                            _(submission.OTHER_DOC_NEEDED_TXT),
                            submission.get_academic_year(now.year-2)),
                submission.VARIABLE_ENROLLMENT_SECONDARY_DIPLOMA_DOC:
                    submission.get_message_secondary_diploma_document(self.applicant),
                submission.VARIABLE_ENROLLMENT_EXAM_ADMISSION_DOC:
                    submission.get_message_exam_admission_document(self.applicant, application_capaes),
                submission.VARIABLE_ENROLLMENT_CAPAES_DOC: _(submission.CAPAES_DOC_NEEDED_TXT),
                submission.VARIABLE_ENROLLMENT_CAPAES_IDENTIFICATION_DOC:
                    submission.get_message_capaes_identification_document(application_capaes.offer_year.grade_type.institutional_grade_type),
                submission.VARIABLE_ENROLLMENT_OPES_DOC: '',
                submission.VARIABLE_ENROLLMENT_FOPA_DOC: '',
                submission.VARIABLE_ENROLLMENT_CAPAES_DATES:
                    submission.get_capaes_dates_paragraph(application_capaes.offer_year.grade_type.institutional_grade_type,
                                                          application_capaes.offer_year.academic_year.year)
                }

        self.assertTrue(submission.message_template_inscription_variables(self.applicant, application_capaes) == data)

    def test_get_variables_for_message_template_for_inscription_opes(self):
        self.applicant.gender = mdl.applicant.MALE

        application_opes = self.create_application_by_acronym('OPES2MS')
        self.create_curriculum_list('OTHER', 2, now.year)
        year_plus_one = application_opes.offer_year.academic_year.year+1
        academic_year = "{0}-{1}".format(str(application_opes.offer_year.academic_year.year), str(year_plus_one))
        data_model.create_curriculum(self.applicant, 'UNEMPLOYMENT')

        self.create_admission_exam_data()
        self.create_data_debts_doc_needed()
        data = {submission.VARIABLE_LAST_NAME: LAST_NAME,
                submission.VARIABLE_FIRST_NAME: FIRST_NAME,
                submission.VARIABLE_REFERENCE: '',
                submission.VARIABLE_ENROLLMENT_OFFER_ACRONYM: application_opes.offer_year.acronym,
                submission.VARIABLE_TITLE: 'Mister',
                submission.VARIABLE_ENROLLMENT_YEAR: application_opes.offer_year.academic_year.year,
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_1: '',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_2: '',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_3: '',
                submission.VARIABLE_RESPONSIBLE: '',
                submission.VARIABLE_ORGANIZATION_NAME: '',
                submission.VARIABLE_ORGANIZATION_STREET: '',
                submission.VARIABLE_ORGANIZATION_CITY: '',
                submission.VARIABLE_ORGANIZATION_COUNTRY: '',
                submission.VARIABLE_CLOSING_DATE: '',
                submission.VARIABLE_ENROLLMENT_UNEMPLOYMENT_DOC: _(submission.UNEMPLOYMENT_DOC_NEEDED_TXT),
                submission.VARIABLE_ENROLLMENT_DEBTS_DOC: _(submission.DEBTS_DOC_NEEDED_TXT),
                submission.VARIABLE_ENROLLMENT_OTHER_ACTIVITIES_DOC: " {0} {1} {2} {3}"
                    .format(_(submission.OTHER_DOC_NEEDED_TXT),
                            submission.get_academic_year(now.year-3),
                            _(submission.OTHER_DOC_NEEDED_TXT),
                            submission.get_academic_year(now.year-2)),
                submission.VARIABLE_ENROLLMENT_SECONDARY_DIPLOMA_DOC: submission.get_message_secondary_diploma_document(self.applicant),
                submission.VARIABLE_ENROLLMENT_EXAM_ADMISSION_DOC: submission.get_message_exam_admission_document(self.applicant, application_opes),
                submission.VARIABLE_ENROLLMENT_CAPAES_DOC: '',
                submission.VARIABLE_ENROLLMENT_CAPAES_IDENTIFICATION_DOC: '',
                submission.VARIABLE_ENROLLMENT_OPES_DOC: _(submission.OPES_URL_TXT),
                submission.VARIABLE_ENROLLMENT_FOPA_DOC: '',
                submission.VARIABLE_ENROLLMENT_CAPAES_DATES: []
                }
        self.assertTrue(submission.message_template_inscription_variables(self.applicant, application_opes) == data)

    def test_get_variables_for_message_template_for_inscription_fopa(self):
        self.applicant.gender = mdl.applicant.MALE

        application_fopa = self.create_application_by_acronym('FOPA2MA')

        data = {submission.VARIABLE_LAST_NAME: LAST_NAME,
                submission.VARIABLE_FIRST_NAME: FIRST_NAME,
                submission.VARIABLE_REFERENCE: '',
                submission.VARIABLE_ENROLLMENT_OFFER_ACRONYM: application_fopa.offer_year.acronym,
                submission.VARIABLE_TITLE: 'Mister',
                submission.VARIABLE_ENROLLMENT_YEAR: application_fopa.offer_year.academic_year.year,
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_1: '',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_2: '',
                submission.VARIABLE_SUBJECT_TO_QUOTA_TXT_3: '',
                submission.VARIABLE_RESPONSIBLE: '',
                submission.VARIABLE_ORGANIZATION_NAME: '',
                submission.VARIABLE_ORGANIZATION_STREET: '',
                submission.VARIABLE_ORGANIZATION_CITY: '',
                submission.VARIABLE_ORGANIZATION_COUNTRY: '',
                submission.VARIABLE_CLOSING_DATE: '',
                submission.VARIABLE_ENROLLMENT_UNEMPLOYMENT_DOC: '',
                submission.VARIABLE_ENROLLMENT_DEBTS_DOC: '',
                submission.VARIABLE_ENROLLMENT_OTHER_ACTIVITIES_DOC: '',
                submission.VARIABLE_ENROLLMENT_SECONDARY_DIPLOMA_DOC: '',
                submission.VARIABLE_ENROLLMENT_EXAM_ADMISSION_DOC: '',
                submission.VARIABLE_ENROLLMENT_CAPAES_DOC: '',
                submission.VARIABLE_ENROLLMENT_CAPAES_IDENTIFICATION_DOC: '',
                submission.VARIABLE_ENROLLMENT_OPES_DOC: '',
                submission.VARIABLE_ENROLLMENT_FOPA_DOC: _(submission.FOPA_URL_TXT),
                submission.VARIABLE_ENROLLMENT_CAPAES_DATES: []
                }

        self.assertTrue(submission.message_template_inscription_variables(self.applicant, application_fopa) == data)

    def create_application_by_institutional_grade_type(self, an_institutional_grade_type):
        application_capaes = data_model.create_application(self.applicant)
        grade_type_capaes = mdl_ref.grade_type.GradeType(
            name='Master complémentaire',
            institutional_grade_type=an_institutional_grade_type)
        grade_type_capaes.save()
        application_capaes.offer_year.grade_type = grade_type_capaes
        application_capaes.offer_year.grade_type.save()
        application_capaes.offer_year.subject_to_quota = True
        application_capaes.save()
        return application_capaes

    def create_curriculum_list(self, an_activity_type, occurence, year):
        cpt = 1
        while cpt <= occurence:
            curriculum = data_model.create_curriculum(self.applicant,an_activity_type)
            curriculum.academic_year = year - (cpt+1)
            curriculum.save()
            cpt = cpt + 1

    def create_application_by_acronym(self, an_acronym):
        offer_opes = data_model.create_offer_year()
        offer_opes.acronym = an_acronym
        offer_opes.grade_type = self.grade_type
        offer_opes.subject_to_quota = False
        application_opes = data_model.create_application(self.applicant)
        application_opes.offer_year = offer_opes
        application_opes.save()
        return application_opes

    def test_send_submission_email_for_admission(self):

        self.application.application_type = application_type.ADMISSION

        try:
            submission.send_soumission_email()
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_send_soumission_email_for_admission"))

    def test_model_message_inscription_fill_in(self):
        data_model.create_message_template(submission.MODEL_INSCRIPTON,
                                           'a_subject',
                                           'test {{title}}',
                                           'PLAIN',
                                           'fr-be')
        self.application.application_type = 'INSCRIPTION'
        application_fopa = self.create_application_by_acronym('FOPA2MA')
        application_fopa.application_type = 'INSCRIPTION'
        submission.text_display(self.applicant, application_fopa)
        print('ici')
