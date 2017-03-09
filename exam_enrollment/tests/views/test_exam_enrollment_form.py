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
import json
import random
import warnings

from unittest.mock import patch, Mock, MagicMock

from django.contrib.auth.models import User, Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase

from base.tests.models import test_student, test_person, test_academic_year, test_offer_year, test_offer_enrollment
from exam_enrollment.views import main


def load_json_file(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def _create_group(name):
    group = Group(name=name)
    group.save()
    return group


class ExamEnrollmentFormTest(TestCase):
    def setUp(self):
        self.academic_year = test_academic_year.create_academic_year()
        group = _create_group('students')
        group.permissions.add(Permission.objects.get(codename='is_student'))
        self.user = User.objects.create_user(username='jsmith', email='jsmith@localhost', password='secret')
        self.user_not_student = User.objects.create_user(username='pjashar', email='pjashar@localhost', password='secret')
        self.user.groups.add(group)
        self.person = test_person.create_person_with_user(self.user, first_name="James", last_name="Smith")
        self.registration_id = "12345678"
        self.student = test_student.create_student_with_registration_person(self.registration_id, self.person)
        offer_year_id = 1234
        self.off_year = test_offer_year.create_offer_year_from_kwargs(**{'id': offer_year_id,
                                                                         'acronym': 'SINF1BA',
                                                                         'title': 'Bechelor in informatica',
                                                                         'academic_year': self.academic_year})
        self.url = "/exam_enrollment/{}/form/".format(offer_year_id)
        self.correct_exam_enrol_form = load_json_file("exam_enrollment/tests/ressources/exam_enrollment_form_example.json")

    def test_json_form_content(self):
        form = self.correct_exam_enrol_form
        self.assertTrue(form.get('registration_id'))
        self.assertTrue(form.get('current_number_session'))
        exam_enrollments = form.get('exam_enrollments')
        self.assertTrue(exam_enrollments)
        random_exam_enrol_position = random.randrange(len(exam_enrollments))
        random_exam_enrol = exam_enrollments[random_exam_enrol_position]
        self.assertTrue('credits' in random_exam_enrol.keys())
        self.assertTrue('credited' in random_exam_enrol.keys())
        self.assertTrue('enrolled_by_default' in random_exam_enrol.keys())
        self.assertTrue('session_1' in random_exam_enrol.keys()
                        or 'session_2' in random_exam_enrol.keys()
                        or 'session_3' in random_exam_enrol.keys())
        self.assertTrue(random_exam_enrol.get('learning_unit_year'))

    @patch("exam_enrollment.views.main._fetch_exam_enrollment_form")
    def test_exam_enrollment_form(self, fetch_json):
        fetch_json.return_value = self.correct_exam_enrol_form
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exam_enrollment_form.html')
        returned_data = response.context[-1]
        self.assertIn('exam_enrollments', returned_data)
        self.assertIn('student', returned_data)
        self.assertIn('current_number_session', returned_data)
        self.assertIn('academic_year', returned_data)
        self.assertIn('program', returned_data)

    @patch("exam_enrollment.views.main._fetch_exam_enrollment_form")
    def test_outside_score_encoding_period(self, fetch_json):
        fetch_json.return_value = None
        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('dashboard_home'))

    def test_case_user_is_not_student(self):
        self.client.force_login(self.user_not_student)
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'access_denied.html')

    @patch("osis_common.queue.queue_sender.send_message")
    def test_exam_enrollment_form_submission_message(self, send_message):
        warnings.warn(
            "The field named 'etat_to_inscr' is only used to call EPC services. It should be deleted when the exam "
            "enrollment business will be implemented in Osis (not in EPC anymore). "
            "The flag 'is_enrolled' should be sufficient for Osis.",
            DeprecationWarning
        )
        send_message.return_value = None
        self.client.force_login(self.user)
        post_data = {
            "chckbox_exam_enrol_sess1_LPHYS1234": "on",
            "etat_to_inscr_current_session_LPHYS1234": "I",
            "chckbox_exam_enrol_sess1_LBIO4567": "",
            "etat_to_inscr_current_session_LBIO4567": "None",
            "chckbox_exam_enrol_sess1_LDROI1111": None,
            "etat_to_inscr_current_session_LDROI1111": None,
            "current_number_session": 1,
        }
        # from django.contrib.messages.storage import default_storage
        # request._messages = default_storage(request)
        exam_enrollments_expected = [{"acronym": "LPHYS1234",
                                      "is_enrolled": True,
                                      "etat_to_inscr": "I"},
                                     {"acronym": "LBIO4567",
                                      "is_enrolled": False,
                                      "etat_to_inscr": None},
                                     {"acronym": "LDROI1111",
                                      "is_enrolled": False,
                                      "etat_to_inscr": None}]
        expected_result = {
            "registration_id": self.registration_id,
            "offer_year_acronym": self.off_year.acronym,
            "year": self.off_year.academic_year.year,
            "exam_enrollments": exam_enrollments_expected
        }
        response = self.client.post(self.url, post_data)
        result = main._exam_enrollment_form_submission_message(self.off_year, response.wsgi_request, self.student)
        self.assertEqual(len(result), len(expected_result))
        self.assertEqual(expected_result.get('registration_id'), result.get('registration_id'))
        self.assertEqual(expected_result.get('offer_year_acronym'), result.get('offer_year_acronym'))
        self.assertEqual(expected_result.get('year'), result.get('year'))
        exam_enrollments = result.get('exam_enrollments')
        exam_enrollments_expected = expected_result.get('exam_enrollments')
        for index in range(0, len(exam_enrollments)):
            self.assertIn(exam_enrollments[index], exam_enrollments_expected)

    def create_offer_enrollment_for_current_academic_yr(self):
        off_year_current_academic_year = test_offer_year.create_offer_year_with_academic_year(
            test_academic_year.create_academic_year_current())
        student_offer_year_enrollment = test_offer_enrollment.create_offer_enrollment(self.student,
                                                                                      off_year_current_academic_year)
        return student_offer_year_enrollment

    def test_get_programs_student_is_none(self):
        self.assertIsNone(main._get_student_programs(None))

    def test_get_one_program(self):
        self.client.force_login(self.user)
        student_offer_year_enrollment = self.create_offer_enrollment_for_current_academic_yr()
        self.assertEqual(main._get_student_programs(self.student)[0], student_offer_year_enrollment.offer_year)

    @patch('base.models.student.find_by_user')
    def test_choose_offer_no_student_for_current_user(self, mock_find_by_user):
        mock_find_by_user.return_value = None

        self.client.force_login(self.user)

        an_url = reverse('exam_enrollment_offer_choice', args=(1, ))
        response = self.client.get(an_url, follow=True)

        self.assertEqual('offer_choice.html', response.templates[0].name)

    @patch('exam_enrollment.views.main._get_student_programs')
    def test_navigation_student_has_no_programs(self, mock_student_programs):
        mock_student_programs.return_value = None

        self.client.force_login(self.user)
        an_url = reverse('exam_enrollment_offer_choice', args=(1,))
        response = self.client.get(an_url, follow=True)
        self.assertRedirects(response, reverse('dashboard_home'))
        self.assertEqual('dashboard.html', response.templates[0].name)

    @patch('exam_enrollment.views.main._get_student_programs')
    @patch('exam_enrollment.views.main._fetch_exam_enrollment_form')
    @patch('base.models.academic_year.current_academic_year')
    @patch('base.models.offer_year.find_by_id')
    def test_navigation_student_has_programs_but_no_data(self,
                                                         mock_find_by_id,
                                                         mock_current_academic_year,
                                                         mock_fetch_exam_form,
                                                         mock_get_student_programs):
        mock_find_by_id.return_value = Mock()
        mock_current_academic_year.return_value = None
        mock_get_student_programs.return_value = [MagicMock(id=1)]
        mock_fetch_exam_form.return_value = None

        self.client.force_login(self.user)
        an_url = reverse('exam_enrollment_offer_choice', args=(1, ))

        response = self.client.get(an_url, follow=True)

        self.assertTrue(mock_current_academic_year.called)
        self.assertRedirects(response, reverse('dashboard_home'))

    @patch('exam_enrollment.views.main._get_student_programs')
    @patch('exam_enrollment.views.main._fetch_exam_enrollment_form')
    @patch('base.models.academic_year.current_academic_year')
    @patch('base.models.offer_year.find_by_id')
    def test_navigation_student_has_programs_with_data(self,
                                                       mock_find_by_id,
                                                       mock_current_academic_year,
                                                       mock_fetch_exam_form,
                                                       mock_get_student_programs):
        mock_find_by_id.return_value = Mock()
        mock_current_academic_year.return_value = None
        mock_get_student_programs.return_value = [MagicMock(id=1)]
        mock_fetch_exam_form.return_value = {
            'exam_enrollments': [],
            'current_number_session': 0,
        }

        self.client.force_login(self.user)
        an_url = reverse('exam_enrollment_offer_choice', args=(1, ))

        response = self.client.get(an_url, follow=True)

        self.assertTrue(mock_current_academic_year.called)
        self.assertEqual('exam_enrollment_form.html', response.templates[0].name)

