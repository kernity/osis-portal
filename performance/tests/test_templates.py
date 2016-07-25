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

from django.test import SimpleTestCase, Client
from base.models import student, person
from django.contrib.auth.models import UserManager


class TemplatesPerformanceTest(SimpleTestCase):
    def setUp(self):
        self.client = Client()
        self.user_manager = UserManager()
        # Create student user
        self.createStudentUser()

    def createStudentUser(self):
        user_student = self.user_manager.create_user("user_student", password="user_pass")
        person_student = person.Person(user=user_student,
                                            global_id="45451000",
                                            first_name="Student",
                                            last_name="Etudiant",
                                            email="student@stud.com")
        self.stud = student.Student(person=person_student,
                                    registration_id="45451000")

    def testHome(self):
        # User is not logged
        response = self.client.get()
