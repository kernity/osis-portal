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
from admission.utils import pdf_submission
from admission.models.enums import application_type
from admission import models as mdl
from reference import models as mdl_ref
from reference.enums import institutional_grade_type as enum_institutional_grade_type
import datetime


LAST_NAME = 'jacob'
FIRST_NAME = 'toto'
MIDDLE_NAME = 'Jules'
BIRTH_PLACE = 'NAMUR'
BELGIUM = 'BELGIUM'
MARRIED = 'MARRIED'
SPOUSE_NAME = 'Maria Theresa'
CHILDREN = 3
DATE_USED = datetime.datetime.now()


class PdfSubmissionTest(TestCase):

    def setUp(self):
        self.applicant = self.create_default_applicant()
        self.application = data_model.create_application(self.applicant)
        activate('en')

    def create_default_applicant(self):
        country_belgium = mdl_ref.country.Country(iso_code='BE', name=BELGIUM)
        country_belgium.save()
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
        applicant.birth_country = country_belgium
        applicant.civil_status = MARRIED
        applicant.spouse_name = SPOUSE_NAME
        applicant.number_children = CHILDREN
        return applicant

    def test_get_identification_data(self):

        data = {pdf_submission.LAST_NAME:       LAST_NAME,
                pdf_submission.FIRST_NAME:      FIRST_NAME,
                pdf_submission.MIDDLE_NAME:     MIDDLE_NAME,
                pdf_submission.BIRTH_DATE:      DATE_USED,
                pdf_submission.BIRTH_PLACE:     BIRTH_PLACE,
                pdf_submission.BIRTH_COUNTRY:   BELGIUM,
                pdf_submission.CIVIL_STATUS:    MARRIED,
                pdf_submission.SPOUSE_NAME:     SPOUSE_NAME,
                pdf_submission.NUMBER_CHILDREN: CHILDREN}

        self.assertTrue(pdf_submission.get_identification_data(self.applicant) == data)

    def test_create_pdf(self):
        try:
            pdf_submission.build_pdf([])
        except:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_pdf"))

