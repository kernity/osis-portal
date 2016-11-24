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
from django.test import TestCase, RequestFactory
import admission.tests.data_for_tests as data_model
from admission.views import application
from admission.models.enums import application_type
from reference.enums import institutional_grade_type as enum_institutional_grade_type
from admission.utils.send_mail import title
from admission import models as mdl


class ApplicationTest(TestCase):
    BASIC_URL_PART1 = 'http://www.uclouvain.be/'
    BASIC_URL_PART2 = '357540.html'

    def setUp(self):
        a_user = User.objects.create_user(
            username='jacob', email='jacob@localhost', password='top_secret')
        self.applicant = data_model.create_applicant_by_user(a_user)
        self.application = data_model.create_application(self.applicant)

    def test_create_application_assimilation_criteria_from_applicant_assimilation_criteria(self):
        data_model.create_applicant_assimilation_criteria(self.applicant)
        try:
            application.create_application_assimilation_criteria(self.application)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!"
                      .format("test_create_application_assimilation_criteria_from_applicant_assimilation_criteria"))

    def test_delete_existing_answers(self):
        try:
            application.delete_existing_answers(self.application)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!"
                      .format("test_create_application_assimilation_criteria_from_applicant_assimilation_criteria"))

    def test_create_answers_txt_question(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'txt_answer_question_1': 'Answer txt question 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_question"))

    def test_create_answers_txt_radio(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'txt_answer_radio_1': 'Answer txt radio 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_radio"))

    def test_create_answers_txt_checkbox(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'txt_answer_checkbox_1': 'Answer txt checkbox 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_checkbox"))

    def test_create_answers_txt_select(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'slt_question_1': 'Answer slt_question_ 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_select"))

    def test_delete_application_assimilation_criteria(self):
        try:
            application.delete_application_assimilation_criteria(self.application)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_select"))

    def test_get_submission_docs_english_url(self):

        basic_url = create_url(BASIC_URL_PART1, BASIC_URL_PART2, None)
        english_url =  create_url(BASIC_URL_PART1, BASIC_URL_PART2, 'en')

        grade_type = data_model.create_grade_type('Master complémentaire',
                                                  enum_institutional_grade_type.ADVANCED_MASTER)

        self.application.offer_year.grade_type = grade_type
        self.application.save()


        self.assertTrue((get_submission_docs_url(self.application.offer_year.grade_type)) == english_url)

    def test_get_title_mr(self):
        self.applicant.gender = mdl.applicant.Applicant.GENDER_CHOICES['MALE']
        self.applicant.save()
        title = get_title(applicant)
        self.assertTrue((title == _('mister'))

    # def test_send_submission_email_for_admission(self):
    #     self.application.application_type = application_type.ADMISSION
    #     self.application.save()
    #
    #     try:
    #         send_soumission_email(self.application)
    #     except Exception:
    #         self.fail("{0} raised ExceptionType unexpectedly!".format("test_send_soumission_email_for_admission"))
    #
    # def test_send_submission_email_for_inscription(self):
    #     self.application.application_type = application_type.INSCRIPTION
    #     try:
    #         application.send_soumission_email(self.application)
    #     except Exception:
    #         self.fail("{0} raised ExceptionType unexpectedly!".format("test_send_soumission_email_for_inscription"))
    #
    # def test_create_submission_pdf(self):
    #     self.application.application_type = application_type.INSCRIPTION
    #     try:
    #         application.send_soumission_email(self.application)
    #     except Exception:
    #         self.fail("{0} raised ExceptionType unexpectedly!".format("test_send_soumission_email_for_inscription"))

def create_url(basic_url_part1, basic_url_part2, language):
    if language == 'en':
        return '{0}en-{1}'.format(basic_url_part1,basic_url_part2)
    else:
        return basic_url_part1 + basic_url_part2

def get_submission_docs_url(grade_type):
    return ""

def get_title(applicant):
    return send_mail.title(applicant.gender)


def send_soumission_email(self.application):
    reference = ""
    title = get_title()
    return None