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
from base import models as mdl_base


TEACHING_CHARGE_APPLICATION = "TEACHING_CHARGE_APPLICATION"


def is_online_application_opened(user):
    application_year = mdl_base.academic_year.find_next_academic_year()
    if application_year:
        an_academic_year = mdl_base.academic_year.find_by_year(application_year)
        if an_academic_year:
            return mdl_base.academic_calendar\
                .is_academic_calendar_opened(an_academic_year, TEACHING_CHARGE_APPLICATION)
    return False
