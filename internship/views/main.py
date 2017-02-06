# -*- coding: utf-8 -*-
############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
############################################################################
from django.contrib.auth.decorators import login_required, permission_required
from base.views import layout
from internship import models as internship_mdl


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_internship_home(request):

    return layout.render(request, "internship_home.html")


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_internship_offers(request):
    internship_types = ["Stage médecine interne", "Stage urgence", "Stage chirurgie", "Stage pédiatrie",
                        "Stage aux choix 1", "Stage aux choix 2", "Stage aux choix 3", "Stage aux choix 4",
                        "Stage aux choix 5", "Stage aux choix 6"]
    specialities = ["médecine interne", "urgence", "chirurgie", "chirurgie", "pédiatrie", "pédopsychiatrie",
                    "radiologie", "chirurgie plastique", "dermatologie"]
    internship_offers = [("Cliniques Universitaires Saint Luc", "Bruxelles", "Dr Ries"),
                         ("Clinique Saint Jean", "Bruxelles", "Dr Brands"),
                         ("Clinique Sainte Elisabeth", "Namur", "Dr Dooms"),
                         (" Clinique Saint Joseph", "Mons", "Dr Lemaire"),
                         ("Hôpital Sint Nikolaus", "Eupen", "Pr Harag")]
    return layout.render(request, "internship_offers.html", {"internship_types": internship_types,
                                                             "specialities": specialities,
                                                             "internship_offers": internship_offers})
