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
import datetime
import logging
import json
import traceback
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from osis_common.document import paper_sheet
from frontoffice.queue import queue_listener
from base import models as mdl_base
from base.views import layout
from dashboard import models as mdl


logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def score_encoding(request):
    return layout.render(request, "score_encoding.html", {})


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def download_papersheet(request):
    person = mdl_base.person.find_by_user(request.user)
    if person:
        pdf = print_scores(person.global_id)
        if pdf:
            filename = "%s.pdf" % _('scores_sheet')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
            response.write(pdf)
            return response
    else:
        logger.warning("A person doesn't exist for the user {0}".format(request.user))

    messages.add_message(request, messages.WARNING, _('no_score_to_encode'))
    return score_encoding(request)


def print_scores(global_id):
    json_document = get_score_sheet(global_id)
    if json_document:
        document = json.loads(json_document)
        try:
            return paper_sheet.build_pdf(document)
        except KeyError:
            trace = traceback.format_exc()
            logger.error(trace)
            logger.warning("A document could not be produced from the json document of the global id {0}".format(global_id))
    else:
        logger.warning("A json document for the global id {0} doesn't exist.".format(global_id))
    return None


def get_score_sheet(global_id):
    scor_encoding = mdl.score_encoding.find_by_global_id(global_id)
    document = None
    if scor_encoding:
        document = scor_encoding.document
    if not document or is_outdated(document):
        document = fetch_document(global_id)
    return document


def fetch_document(global_id):
    json_data = fetch_json(global_id)
    if json_data:
        return mdl.score_encoding.insert_or_update_document(global_id, json_data).document
    else:
        return None


def fetch_json(global_id):
    try:
        scores_sheets_cli = queue_listener.ScoresSheetClient()
        json_data = scores_sheets_cli.call(global_id)
        if json_data:
            json_data = json_data.decode("utf-8")
    except Exception:
        json_data = None
        trace = traceback.format_exc()
        logger.error(trace)

    return json_data


def is_outdated(document):
    json_document = json.loads(document)
    now = datetime.datetime.now()
    now_str = '%s/%s/%s' % (now.day, now.month, now.year)
    if json_document.get('publication_date', None) != now_str:
            return True
    return False
