##############################################################################
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
##############################################################################
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle,Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from django.utils.translation import ugettext_lazy as _
import datetime
from admission import models as mdl

from base import models as mdl_base
from admission.views import submission


PAGE_SIZE = A4
MARGIN_SIZE = 15 * mm
COLS_WIDTH = [20*mm, 55*mm, 45*mm, 15*mm, 40*mm]
COLS_WIDTH_IDENTIFICATION = [45*mm, 90*mm]
COLS_WIDTH_CONTACT = [45*mm, 130*mm]
COLS_WIDTH_NATIONAL_EDUCATION = [95*mm, 80*mm]
COLS_WIDTH_SECONDARY_RESULT = [100*mm, 75*mm]
COLS_WIDTH_IDENTIFICATION_MAIN = [140*mm, 35*mm]
STUDENTS_PER_PAGE = 24
COLS_WIDTH_INSTITUTION = [175*mm]
COLS_WIDTH_CURRICULUM = [45*mm, 45*mm, 45*mm, 25*mm]
COLS_WIDTH_CURRICULUM_STUDIES = [35*mm, 140*mm]


LAST_NAME = 'last_name'
FIRST_NAME = 'first_name'
MIDDLE_NAME = 'middle_name'
BIRTH_DAY = 'birth_day'
BIRTH_PLACE = 'birth_place'
BIRTH_COUNTRY = 'birth_country'
CIVIL_STATUS = 'civil_status'
SPOUSE_NAME = 'spouse_name'
CHILDREN = 'children'

MOBILE = 'mobile'
ADDITIONAL_EMAIL = 'additional_email'

class MCLine(Flowable):
    """
    Line flowable --- draws a line in a flowable
    http://two.pairlist.net/pipermail/reportlab-users/2005-February/003695.html
    """

    #----------------------------------------------------------------------
    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    #----------------------------------------------------------------------
    def __repr__(self):
        return "Line(w=%s)" % self.width

    #----------------------------------------------------------------------
    def draw(self):
        """
        draw the line
        """
        self.canv.line(0, self.height, self.width, self.height)

def add_header_footer(canvas, doc):
    """
    Add the page number
    """
    styles = getSampleStyleSheet()
    # Save the state of our canvas so we can draw on it
    canvas.saveState()

    # Header
    header_building(canvas, doc, styles)

    # Footer
    footer_building(canvas, doc, styles)

    # Release the canvas
    canvas.restoreState()


def build_pdf(data):
    application = None
    applicant = None
    contact_address = None
    legal_address = None
    secondary_education = None
    if 'application' in data:
        application = data['application']
        applicant = application.applicant
    if 'contact_address' in data:
        contact_address = data['contact_address']
    if 'legal_address' in data:
        legal_address = data['legal_address']
    if 'secondary_education' in data:
        secondary_education = data['secondary_education']
    curriculum_studies = []
    if 'curriculum_studies' in data:
        curriculum_studies = data['curriculum_studies']
    curriculum_others = []
    if 'curriculum_others' in data:
        curriculum_others = data['curriculum_others']

    filename = "%s.pdf" % _('submission')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=PAGE_SIZE,
                            rightMargin=MARGIN_SIZE,
                            leftMargin=MARGIN_SIZE,
                            topMargin=85,
                            bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='picture',
                              parent=styles['Normal'],
                              borderWidth=1,
                              borderColor=colors.black,
                              borderPadding=5,))
    styles.add(ParagraphStyle(name='bold',
                              parent=styles['Normal'],
                              fontName='Times-Bold'
                              ))
    styles.add(ParagraphStyle(name='italic-underline',
                              parent=styles['Normal'],
                              fontName='Times-Italic',
                              underlineProportion=3
                              ))

    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='red',
                              textColor=colors.red,
                              parent=styles['Normal'],))
    content = []
    write_pdf_title(content, styles)
    write_explanation_block(content, styles)
    write_identification_block(content, styles, applicant)
    add_space_between_lines(content, styles)
    write_contact_block(content, styles, applicant)
    add_space_between_lines(content, styles)
    write_addresses_block(content, styles, contact_address, legal_address)
    if secondary_education and secondary_education.diploma:
        write_secondary_education_block(content, styles, secondary_education)
    print(len(curriculum_studies))
    if len(curriculum_studies) > 0:
        write_curriculum_studies_block(content, styles, curriculum_studies)
    if len(curriculum_others) > 0:
        write_curriculum_others_block(content, styles, curriculum_others)
    doc.build(content, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def add_space_between_lines(content, styles):
    content.append(Paragraph('''
                            <para>
                                &nbsp;
                            </para>
                            ''', styles['Normal']))


def write_identification_block(content, styles, applicant):
    identification_data = set_identification_data(applicant, styles)
    identification_data_and_picture = \
        [[_write_table_identification(identification_data),
          Paragraph(_('glue_id_picture'), styles['picture'])]]
    _write_table_identification_main(content, identification_data_and_picture)


def write_contact_block(content, styles, applicant):
    contact_data = set_contact_data(applicant, styles)
    _write_table_contact(content, contact_data)

def get_academic_year(an_academic_year):
    return "{0}-{1}".format(an_academic_year , an_academic_year+1)

def write_secondary_education_block(content, styles, secondary_education):
    add_space_between_lines(content, styles)
    content.append(
        Paragraph(_('secondary_education'), styles['Heading2']))
    data = []
    data.append(["{0}:".format(_('academic_year')),
                 get_academic_year(secondary_education.academic_year)])
    write_secondary_education_year_block(content, data)
    add_space_between_lines(content, styles)
    if secondary_education.national is True:
        national_data = get_national_secondary_data(secondary_education, styles)
        write_secondary_education_national_block(content, national_data)
    else:
        foreign_data = get_foreign_secondary_data(secondary_education, styles)
        write_secondary_education_foreign_block(content, foreign_data)
    add_space_between_lines(content, styles)

    result = ''
    if secondary_education.result:
        result=  _("{0}_result".format(secondary_education.result.lower()))
        result = result.lower()
    write_secondary_education_result_block(content, [[_('high_school_result'),
                                                      result]])
    if secondary_education.national is True:
        add_space_between_lines(content, styles)
        institution_data = set_institution_data(secondary_education.national_institution, styles)
        _write_table_institution(content, institution_data)


def write_secondary_education_year_block(content, data):
    t = Table(data, COLS_WIDTH_CONTACT, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def write_addresses_block(content, styles, contact_address, legal_address):
    address_data = []
    set_block_header(address_data, styles, _('addresses'))
    set_address_data(contact_address, styles, address_data)
    address_data.append(["{0}".format(''), ],)
    set_address_data(legal_address, styles, address_data)
    _write_table_address(content, address_data)


def set_identification_data(applicant, styles):
    data = []
    set_block_header(data, styles, _('identification'))
    data.append(["{0} :".format(_('lastname')), format_string_for_display(applicant.user.last_name)],)
    data.append(["{0} :".format(_('firstname')), format_string_for_display(applicant.user.first_name)],)
    data.append(["{0} :".format(_('middle_name')), format_string_for_display(applicant.middle_name)],)
    data.append(["{0} :".format(_('birth_day')), format_date_for_display(applicant.birth_date)],)
    data.append(["{0} :".format(_('birth_place')), format_string_for_display(applicant.birth_place)],)
    if applicant.birth_country:
        data.append(["{0} :".format(_('birth_country')), format_string_for_display(applicant.birth_country.name)],)
    print(applicant.civil_status)
    print(_(applicant.civil_status))
    data.append(["{0} :".format(_('civil_status')), format_string_for_display_trans(applicant.civil_status)],)
    data.append(["{0} :".format(_('spouse_name')), format_string_for_display(applicant.spouse_name)],)
    data.append(["{0} :".format(_('children')), format_string_for_display(str(applicant.number_children))],)
    return data


def set_contact_data(applicant, styles):
    data = []
    set_block_header(data, styles, _('contact'))
    data.append(["{0} :".format(_('mobile')), format_string_for_display(applicant.phone_mobile)],)
    data.append(["{0} :".format(_('mail')), format_string_for_display(applicant.additional_email)],)
    return data


def format_street_string(address):
    street = ''
    if address:
        if address.street:
            street += address.street
            if address.number:
                street += ', '
        if address.number:
            street += address.number
        if address.complement:
            street += address.complement

    return street


def set_address_data(address, styles, data):
    address_type = ''
    street = ''
    postal_code = ''
    city = ''
    country = ''
    if address:
        address_type = address.type
        street = format_string_for_display(format_street_string(address))
        postal_code = format_string_for_display(address.postal_code)
        city = format_string_for_display(address.city)
        country = ''
        if address.country:
            country = address.country.name
    if type != '':
        data.append([Paragraph(address_type, styles['Heading3']), ],)
    data.append(["{0} :".format(_('street')), street],)
    data.append(["{0} :".format(_('postal_code')), postal_code],)
    data.append(["{0} :".format(_('city')), city],)
    data.append(["{0} :".format(_('country')), country],)
    return data


def set_block_header(data, styles, title):
    data.append([
        Paragraph(title, styles['Heading2'])], )


def set_block_header_style(data, styles, title, style):
    data.append([
        Paragraph(title, styles[style])], )


def get_identification_data(an_applicant):
    data = {LAST_NAME:       an_applicant.user.last_name,
            FIRST_NAME:      an_applicant.user.first_name,
            MIDDLE_NAME:     format_string_for_display(an_applicant.middle_name),
            BIRTH_DAY:      an_applicant.birth_date,
            BIRTH_PLACE:     an_applicant.birth_place,
            BIRTH_COUNTRY:   an_applicant.birth_country.name,
            CIVIL_STATUS:    format_string_for_display(_(an_applicant.civil_status)),
            SPOUSE_NAME:     format_string_for_display(an_applicant.spouse_name),
            CHILDREN: format_number_for_display(an_applicant.number_children)}
    return data


def get_contact_data(an_applicant):
    data = {MOBILE:           an_applicant.phone_mobile,
            ADDITIONAL_EMAIL: an_applicant.additional_email}
    return data


def format_string_for_display(string):
    if string is None:
        return ''
    else:
        return string.strip()


def format_string_for_display_trans(string):
    return _(format_string_for_display(string.lower()))


def format_number_for_display(number):
    if number is None:
        return ''
    return str(number)


def get_secondary_education(an_applicant):
    return mdl.secondary_education.find_by_person(an_applicant)


def get_secondary_exam(a_secondary_education, a_type):
    return mdl.secondary_education_exam.find_by_type(a_secondary_education, a_type)


def get_curriculum_list(an_applicant, path_types):
    return mdl.curriculum.find_by_path_type_list_order_by_desc_academic_year(an_applicant, path_types)


def get_sociological_survey(an_applicant):
    return mdl.sociological_survey.find_by_applicant(an_applicant)


def get_person_address(an_applicant, a_type):
    return mdl.person_address.find_by_person_type(an_applicant, a_type)


def test(request):
    application = mdl.application.find_first_by_user(request.user)

    return build_pdf({'application': application,
                      'contact_address': get_person_address(application.applicant, 'CONTACT'),
                      'legal_address': get_person_address(application.applicant, 'LEGAL'),
                      'secondary_education': get_secondary_education(application.applicant),
                      'curriculum_studies': get_curriculum_list(application.applicant, ['LOCAL_UNIVERSITY',
                                                                                        'FOREIGN_UNIVERSITY',
                                                                                        'LOCAL_HIGH_EDUCATION',
                                                                                        'FOREIGN_HIGH_EDUCATION']),
                      'curriculum_others': get_curriculum_list(application.applicant, ['ANOTHER_ACTIVITY'])})


def header_building(canvas, doc, styles):
    a = Image(settings.LOGO_INSTITUTION_URL, width=15*mm, height=20*mm)

    enrollment_application_title = Paragraph('''<para align=center>
                        <font size=16>%s</font>
                    </para>''' % (_('enrollment_application')), styles["BodyText"])

    data_header = [[a, '%s' % _('ucl_denom_location'), enrollment_application_title], ]

    t_header = Table(data_header, [30*mm, 100*mm, 50*mm])

    t_header.setStyle(TableStyle([]))

    w, h = t_header.wrap(doc.width, doc.topMargin)
    t_header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)


def footer_building(canvas, doc, styles):
    printing_date = datetime.datetime.now()
    printing_date = printing_date.strftime("%d/%m/%Y")
    pageinfo = "%s : %s" % (_('printing_date'), printing_date)
    footer = Paragraph(''' <para align=right>Page %d - %s </para>''' % (doc.page, pageinfo), styles['Normal'])
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin, h)


def end_page_infos_building(content, end_date):
    p = ParagraphStyle('info')
    p.fontSize = 10
    p.alignment = TA_LEFT
    if not end_date:
        end_date = '(%s)' % _('date_not_passed')
    content.append(Paragraph(_("return_doc_to_administrator") % end_date
                             , p))
    content.append(Paragraph('''
                            <para spaceb=5>
                                &nbsp;
                            </para>
                            ''', ParagraphStyle('normal')))
    p_signature = ParagraphStyle('info')
    p_signature.fontSize = 10
    paragraph_signature = Paragraph('''
                    <font size=10>%s ...................................... , </font>
                    <font size=10>%s ..../..../.......... &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font>
                    <font size=10>%s</font>
                   ''' % (_('done_at'), _('the'), _('signature')), p_signature)
    content.append(paragraph_signature)
    content.append(Paragraph('''
        <para spaceb=2>
            &nbsp;
        </para>
        ''', ParagraphStyle('normal')))


def _write_table_identification(data):
    cc = []
    t = Table(data, COLS_WIDTH_IDENTIFICATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    cc.append(t)
    return cc


def _write_table_identification_main(content, data):
    t = Table(data, COLS_WIDTH_IDENTIFICATION_MAIN, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def _write_table_contact(content, data):

    t = Table(data, COLS_WIDTH_CONTACT, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def _write_table_address(content, data):

    t = Table(data, COLS_WIDTH_CONTACT, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def get_national_secondary_data(secondary_education, styles):
    data = []
    set_block_header(data, styles, _('high_school'))
    national_community_str = ''
    if secondary_education.national_community:
        national_community_str = secondary_education.national_community
    education_type_str = ''
    if secondary_education.education_type:
        education_type_str = secondary_education.education_type.name

    data.append(["{0} :".format(_('diploma_national_community')), Paragraph(national_community_str, styles['bold'])],)
    data.append(["{0} :".format(_('teaching_type')), Paragraph(education_type_str, styles['bold'])],)

    data_current_studies = []
    data_current_studies.append([Paragraph("{0} :".format(_('current_studies')), styles['bold'])],)
    data_current_studies.append(["  {0} :".format(_('repetition')), format_yes_no(secondary_education.path_repetition)],)
    data_current_studies.append(["  {0} :".format(_('reorientation')),
                                 format_yes_no(secondary_education.path_reorientation)],)

    data.append([_write_table_current_studies(data_current_studies), ''],)
    return data


def write_secondary_education_national_block(content, data):
    t = Table(data, COLS_WIDTH_NATIONAL_EDUCATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def format_yes_no(boolean_value):
    if boolean_value is True:
        return _('yes')
    if boolean_value is False:
        return _('no')
    return ''


def _write_table_current_studies(data):
    cc = []
    t = Table(data, COLS_WIDTH_IDENTIFICATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    cc.append(t)
    return cc


def get_foreign_secondary_data(secondary_education, styles):
    data = []
    set_block_header(data, styles, _('national_secondary_education'))
    international_diploma_title = ''
    if secondary_education.international_diploma:
        international_diploma_title = secondary_education.international_diploma
    international_diploma_language_str = ''
    if secondary_education.international_diploma_language:
        international_diploma_language_str = secondary_education.international_diploma_language.name
    equivalence_str = ''
    if secondary_education.international_equivalence:
        equivalence_str = secondary_education.international_equivalence
    data.append(["{0} :".format('Intitulé du diplôme obtenu'),
                 Paragraph(international_diploma_title, styles['bold'])],)
    data.append(["{0} :".format('Régime linguistique dans lequel le diplôme a été obtenu'),
                 Paragraph(international_diploma_language_str, styles['bold'])],)
    data.append(["{0} :".format('Equivalence reconnue par la Communauté française de Belgique'),
                 Paragraph(equivalence_str, styles['bold'])],)
    return data


def write_secondary_education_foreign_block(content, data):
    t = Table(data, COLS_WIDTH_NATIONAL_EDUCATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def write_secondary_education_result_block(content, data):
    print(data)

    t = Table(data, COLS_WIDTH_NATIONAL_EDUCATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def set_institution_data(education_institution, styles):
    data = []
    if education_institution:
        set_block_header_style(data, styles,
                               "{0} :".format(_('high_school_institute')), 'Italic')
        data.append([format_string_for_display(education_institution.name)],)
        locality = ''
        if education_institution.postal_code:
            locality += education_institution.postal_code
            if education_institution.city:
                locality += ' '
        if education_institution.city:
            locality += education_institution.city

        data.append([locality],)
    return data


def _write_table_institution(content, data):
    t = Table(data, COLS_WIDTH_INSTITUTION, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def write_curriculum_studies_block(content, styles, curriculum):
    add_space_between_lines(content, styles)
    content.append(
        Paragraph(_('curriculum'), styles['Heading2']))
    add_space_between_lines(content, styles)
    for cv in curriculum:
        data = get_curriculum_data(cv, styles)
        write_curriculum_study_block(content, data)


def get_curriculum_data(curriculum, styles):
    data = []
    data.append([
        Paragraph("{0}:".format(submission.get_academic_year(curriculum.academic_year)), styles['Heading2']),
        Paragraph("{0}".format(curriculum.path_type), styles['Heading2'])], )
    national_education = ''
    domain = ''
    grade_type = ''

    national_institution_name = ''
    national_institution_postal_code = ''
    national_institution_city = ''
    if curriculum.national_education:
        national_education = curriculum.national_education
    if curriculum.domain:
        domain = curriculum.domain.name
    if curriculum.grade_type:
        grade_type = curriculum.grade_type
    if curriculum.national_institution:
        national_institution_name = curriculum.national_institution.name
        national_institution_postal_code = curriculum.national_institution.postal_code
        national_institution_city = curriculum.national_institution.city

    data.append(["{0} :".format('Communauté'),
                 Paragraph(national_education, styles['bold'])],)
    data.append(["{0} :".format('Domaine'), Paragraph(domain, styles['bold'])],)
    data.append(["",
                 Paragraph('', styles['Normal'])],)
    data.append(["{0} :".format('Etablissement'),
                 Paragraph(national_institution_name, styles['bold'])],)
    data.append(["",
                 Paragraph("{0} {1}".format(national_institution_postal_code, national_institution_city), styles['bold'])],)
    #
    #
    data_curriculum_detail = []
    data_curriculum_detail.append(["{0}:".format(_('result')), curriculum.result, "{0}:".format('Crédits inscrits'), curriculum.credits_enrolled],)
    data_curriculum_detail.append(["{0}:".format(_('diploma')), format_yes_no(curriculum.diploma), "{0}:".format('Crédits acquis'), curriculum.credits_obtained],)

    data.append([_write_table_curriculum_detail(data_curriculum_detail), ''],)

    return data


def _write_table_curriculum_detail(data):
    cc = []
    t = Table(data, COLS_WIDTH_IDENTIFICATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    cc.append(t)
    return cc


def write_curriculum_study_block(content, data):
    t = Table(data, COLS_WIDTH_CURRICULUM_STUDIES, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white)]))
    content.append(t)


def write_curriculum_others_block(content, styles, curriculum):
    add_space_between_lines(content, styles)
    for cv in curriculum:
        data = get_curriculum_other_data(cv, styles)
        write_curriculum_study_block(content, data)


def get_curriculum_other_data(curriculum, styles):
    data = []
    data.append([
        Paragraph("{0} :".format(submission.get_academic_year(curriculum.academic_year)), styles['Heading2']),
        Paragraph("{0}".format(curriculum.path_type), styles['Heading2'])], )
    activity_type = ''

    if curriculum.activity_type:
        activity_type = curriculum.activity_type

    data.append(["{0} :".format('Activité'),
                 Paragraph(activity_type, styles['bold'])],)
    if curriculum.activity_place:
        data.append(["{0} :".format('Endroit'),
                     Paragraph(curriculum.activity_place, styles['bold'])],)

    return data

def write_pdf_title(content, styles):
    line = MCLine(500)
    content.append(line)
    enrollment_application_explanation = Paragraph('''<para>
                        <font size=16>%s</font>
                    </para>''' % (_('enrollment_application')), styles["BodyText"])
    content.append(enrollment_application_explanation)


def write_explanation_block(content, styles):
    add_space_between_lines(content, styles)
    enrollment_application_explanation = Paragraph('''<para>
                        <font size=12>%s</font>
                    </para>''' % (_('enrollment_application_explanation')), styles["BodyText"])
    content.append(enrollment_application_explanation)
    attention = Paragraph('''<para>
                            <font size=12>%s :</font>
                        </para>''' % (_('attention')), styles["BodyText"])
    content.append(attention)
    enrollment_application_no_recto_verso = Paragraph('''<para>
                        <font size=12>%s</font>
                    </para>''' % (_('no_recto_verso')), styles["red"])
    content.append(enrollment_application_no_recto_verso)
    enrollment_application_not_incomplete = Paragraph('''<para>
                        <font size=12>%s</font>
                    </para>''' % (_('not_incomplete')), styles["red"])
    content.append(enrollment_application_not_incomplete)
    add_space_between_lines(content, styles)


def format_date_for_display(a_date):
    if a_date is None:
        return ''
    else:
        return a_date.strftime('%d/%m/%Y')

