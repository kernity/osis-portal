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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from admission import models as mdl


def get_reference(application, applicant):
    ref_year = get_year_reference(application)
    ref_id = application.id
    applications = mdl.application.find_by_user(applicant.user)
    ref_seq_number = None
    if applications.exists():
        ref_seq_number = len(applications)

    return "{0}-{1}-{2}-{3}".format(get_initials_reference(),
                                    get_year_reference(application),
                                    get_id_reference(application),
                                    ref_seq_number)

def get_year_reference(application):
    ref_year = application.offer_year.academic_year.year
    if ref_year:
        try:
            return str(ref_year)[2:4]
        except:
            return None
    return None


def get_initials_reference():
    return "XX"


def get_id_reference(application):
    return "{0:06}".format(application.id)