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

"""
Utility files for mail sending
"""
import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from frontoffice.settings import DEFAULT_FROM_EMAIL, LOGO_OSIS_URL, LOGO_EMAIL_SIGNATURE_URL
from frontoffice import settings
from osis_common.messaging import send_message
from base.models import academic_year

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def send_mail_activation(request, activation_code, applicant, template_reference):
    logger.info('Sending mail activation to : {} '.format(applicant.user.email))
    message_content = {'html_template_ref': '{0}_html'.format(template_reference),
                       'txt_template_ref': '{0}_txt'.format(template_reference)}
    receivers = []
    receiver = {'receiver_email': applicant.user.email,
                'receiver_id': applicant.id}
    receivers.append(receiver)
    message_content['receivers'] = receivers
    activation_link = "{0}://{1}/admission/admission/user/{2}/activation".format(request.scheme,
                                                                                 request.get_host(),
                                                                                 activation_code)
    data = {'title': title(applicant.gender),
            'academic_year': academic_year.current_academic_year(),
            'activation_link': activation_link,
            'signature': render_to_string('messaging/html_email_signature.html',
                                          {'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                                           'logo_osis_url': LOGO_OSIS_URL})}

    message_content['template_base_data'] = data

    return send_message.send_messages(message_content)


def new_password(request, activation_code, email):
    logger.info('Sending new password to : {} '.format(email))
    activation_link = request.scheme \
                      + "://" + request.get_host() \
                      + "/admission/admission/new_password_form/" \
                      + activation_code
    subject = 'UCL - Votre code d\'activation pour la modification du mot de passe de votre compte.'
    html_message = ''.join([
        EMAIL_HEADER,
        str('<p>Bonjour, </p>'),
        str('<br><br>'),
        str('Pour modifier votre mot de passe merci de cliquer sur le lien suivant :<br><br>'),
        str('<a href="%s">%s</a>') % (activation_link, activation_link),
        str('<br><br>'),
        str('Le service des inscription de l\'UCL<br><br>'),
        str('<a href=\'http://www.uclouvain.be/inscriptionenligne\'>http://www.uclouvain.be/inscriptionenligne</a>'),
        EMAIL_SIGNATURE,
        EMAIL_FOOTER
    ])

    message = ''.join([
        str('Bonjour, \n\n'),
        str('Pour modifier votre mot de passe merci de cliquer sur le lien suivant :\n\n'),
        str(activation_link),
        str('\n'),
        str('Le service des inscription de l\'UCL\n\n'),
        str('http://www.uclouvain.be/inscriptionenligne')
    ])
    if not settings.EMAIL_PRODUCTION_SENDING:
        receiver = settings.COMMON_EMAIL_RECEIVER
    else:
        receiver = email
    send_mail(subject=subject,
              message=message,
              recipient_list=[receiver],
              html_message=html_message,
              from_email=DEFAULT_FROM_EMAIL)

EMAIL_HEADER = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=iso-8859-1"><title>signature</title>
    </head>
    <body>
"""

EMAIL_SIGNATURE = """

        <table cellpadding="5" cellspacing="5">
            <tbody>
                <tr>
                    <td width="60">
                        <img src="http://www.uclouvain.be/cps/ucl/doc/ac-arec/images/logo-signature.png">
                    </td>
                    <td>
                        <img src="https://osis.uclouvain.be/static/img/logo_osis.png">
                    </td>
                </tr>
            </tbody>
        </table>

"""

EMAIL_FOOTER = """
    </body>
</html>
"""


def title(gender):
    if gender == "MALE":
        return _('mister')
    if gender == "FEMALE":
        return _('miss')
    return _('miss') + ", " + _('mister')
