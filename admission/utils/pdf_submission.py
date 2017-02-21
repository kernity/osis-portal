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
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, PageBreak, Table, TableStyle, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line
from django.utils.translation import ugettext_lazy as _
import datetime
from admission import models as mdl

from base import models as mdl_base
from admission.views import submission
from reportlab.lib import *
from functools import partial
from admission.models.enums import application_type
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


BOX_BORDER_SIZE = 0.25
DEFAULT_FONT = 'default_font'

PAGE_SIZE = A4
MARGIN_SIZE = 15 * mm
COL_MAX = [180*mm]
COLS_WIDTH = [20*mm, 55*mm, 45*mm, 15*mm, 40*mm]
COLS_WIDTH_IDENTIFICATION = [45*mm, 100*mm]
COLS_WIDTH_CONTACT = [45*mm, 135*mm]
COLS_WIDTH_NATIONAL_EDUCATION = [95*mm, 85*mm]
COLS_WIDTH_INTERNATIONAL_EDUCATION = [105*mm, 75*mm]
COLS_WIDTH_SECONDARY_RESULT = [100*mm, 80*mm]
COLS_WIDTH_IDENTIFICATION_MAIN = [130*mm, 40*mm, 10*mm]
STUDENTS_PER_PAGE = 24
COLS_WIDTH_INSTITUTION = [175*mm]
COLS_WIDTH_CURRICULUM = [45*mm, 45*mm, 45*mm, 25*mm]
COLS_WIDTH_CURRICULUM_STUDIES = [35*mm, 145*mm]
COLS_WIDTH_SURVEY = [40*mm, 140*mm]
COLS_WIDTH_SIGNATURE = [175*mm]
COLS_WIDTH_SIGNATURE_ATTENTION = [50*mm, 75*mm, 50*mm]
COLS_WIDTH_ACCESS_PICTURE = [70*mm, 75*mm]
COLS_WIDTH_CURRICULUM_RESULTS = [35*mm, 43.75*mm, 43.75*mm, 43.75*mm]
COLS_WIDTH_SECONDARY_YEAR = [55*mm, 125*mm]
COLS_WIDTH_CURRENT_STUDIES = [55*mm, 80*mm]
COLS_WIDTH_SECONDARY_EXAM = [45*mm, 135*mm]


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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTENTION_ICON_URL = os.path.join(BASE_DIR, "static/img/attention_icon.png")
ACCESS_PICTURE_PLACEMENT_URL = os.path.join(BASE_DIR, "static/img/access_picture_placement.png")
# Register Fonts

# pdfmetrics.registerFont(TTFont('Arial', os.path.join(BASE_DIR, "static/fonts/arial.ttf")))
#
# pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(BASE_DIR, "static/fonts/ariali.ttf")))
#
# pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(BASE_DIR, "static/fonts/arialbd.ttf")))
#
# pdfmetrics.registerFont(TTFont('Arial-bi', os.path.join(BASE_DIR, "static/fonts/arialbi.ttf")))
NORMAL_FONT_NAME = 'Times'
ITALIC_FONT_NAME = 'Times-Italic'
BOLD_FONT_NAME = 'Times-Bold'

TABLE_STYLE_INNER_BLOCK = TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0),
                                      ('TOPPADDING', (0, 0), (-1, -1), 0.25),
                                      ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                      ('VALIGN', (0, 0), (-1, -1), 'TOP')])


class MCLine(Flowable):
    """
    Line flowable --- draws a line in a flowable
    http://two.pairlist.net/pipermail/reportlab-users/2005-February/003695.html
    """

    # ----------------------------------------------------------------------
    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "Line(w=%s)" % self.width

    # ----------------------------------------------------------------------
    def draw(self):
        """
        draw the line
        """
        self.canv.line(0, self.height, self.width, self.height)


def add_header_footer(canvas, doc, custom_data=None):
    """
    Add the page number
    """
    styles = getSampleStyleSheet()
    # Save the state of our canvas so we can draw on it
    canvas.saveState()

    # Header
    header_building(canvas, doc, custom_data)

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
    sociological_survey = None
    student = None
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
    if 'sociological_survey' in data:
        sociological_survey = data['sociological_survey']
    if 'student' in data:
        student = data['student']
    filename = "%s.pdf" % _('submission')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=PAGE_SIZE,
                            rightMargin=MARGIN_SIZE,
                            leftMargin=MARGIN_SIZE,
                            topMargin=125,
                            bottomMargin=18)

    styles = custom_styles()

    content = []
    write_pdf_title(content, styles, application.application_type)
    write_explanation_block(content, styles)
    write_identification_block(content, styles, applicant)
    add_space_between_lines(content, styles)
    write_contact_block(content, styles, applicant)
    write_application(content, styles, application, applicant.nationality)
    add_space_between_lines(content, styles)
    write_addresses_block(content, styles, contact_address, legal_address)

    if secondary_education and secondary_education.diploma:
        write_secondary_education_block(content, styles, secondary_education)

    if len(curriculum_studies) > 0:
        write_curriculum_studies_block(content, styles, curriculum_studies)
    if len(curriculum_others) > 0:
        write_curriculum_others_block(content, styles, curriculum_others)
    if secondary_education:
        secondary_education_exam_language = mdl.secondary_education_exam.find_by_type(secondary_education, 'LANGUAGE')
        if secondary_education_exam_language:
            write_secondary_education_exam_block(content,
                                                 styles,
                                                 secondary_education_exam_language,
                                                 _('local_language_exam'))
        else:
            write_secondary_no_education_exam_block(content, styles, _('local_language_exam'))
        secondary_education_exam_admission = mdl.secondary_education_exam.find_by_type(secondary_education, 'ADMISSION')
        if secondary_education_exam_admission:
            write_secondary_education_exam_block(content,
                                                 styles,
                                                 secondary_education_exam_admission,
                                                 _('admission_exam_studies'))
        else:
            write_secondary_no_education_exam_block(content, styles, _('admission_exam_studies'))
    if sociological_survey:
        write_sociological_survey_block(content, styles, sociological_survey)
    write_signature_block(content, styles)
    write_card_block(content, styles)
    write_rules_block(content, styles, applicant)
    header_data = set_header_data(application, applicant, student)
    doc.build(content, onFirstPage=partial(add_header_footer, custom_data=header_data),
              onLaterPages=partial(add_header_footer, custom_data=header_data), canvasmaker=NumberedCanvas)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def custom_styles():
    styles = getSampleStyleSheet()
    # styles.add(ParagraphStyle(name='picture',
    #                           parent=styles['Normal'],
    #                           borderWidth=1,
    #                           borderColor=colors.black,
    #                           borderPadding=5, ))
    styles.add(ParagraphStyle(name='bold',
                              parent=styles['Normal'],
                              fontName=ITALIC_FONT_NAME
                              ))
    styles.add(ParagraphStyle(name='italic-underline',
                              parent=styles['Normal'],
                              fontName=ITALIC_FONT_NAME,
                              underlineProportion=3
                              ))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='red',
                              textColor=colors.red,
                              parent=styles['Normal'], ))
    styles.add(ParagraphStyle(name='paragraph_bordered',
                              parent=styles['Normal'],
                              borderWidth=0.25,
                              borderColor=colors.black,
                              borderPadding=5,
                              ))
    styles.add(ParagraphStyle(name=DEFAULT_FONT,
                              parent=styles['Normal'],
                              fontName=NORMAL_FONT_NAME,
                              fontSize=10
                              ))
    styles.add(ParagraphStyle(name='italic',
                              parent=styles['Normal'],
                              fontName=ITALIC_FONT_NAME
                              ))
    styles.add(ParagraphStyle(name='block_title',
                              parent=styles['Normal'],
                              fontName=ITALIC_FONT_NAME,
                              fontSize=12
                              ))
    styles.add(ParagraphStyle(name='block_sub_title',
                              parent=styles['Normal'],
                              fontName=NORMAL_FONT_NAME,
                              fontSize=12
                              ))
    styles.add(ParagraphStyle(name='header_text',
                              parent=styles['Normal'],
                              fontSize=8
                              ))
    styles.add(ParagraphStyle(name='block_header',
                              parent=styles['Heading2']
                              ))
    styles.add(ParagraphStyle(name='paragraph_bordered_left_indent',
                              parent=styles['paragraph_bordered'],
                              borderWidth=0.25,
                              borderColor=colors.black,
                              borderPadding=5,
                              leftIndent=5,
                              ))


    return styles


def add_space_between_lines(content, styles):
    content.append(Paragraph('''<para>
                                &nbsp;
                            </para>
                            ''', styles[DEFAULT_FONT]))


def write_identification_block(content, styles, applicant):
    identification_data = set_identification_data(applicant, styles)
    table_picture_place = Table([[Paragraph("{0}".format(_('glue_id_picture')), styles[DEFAULT_FONT])]], [35*mm], rowHeights=(45*mm))
    table_picture_place.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))

    identification_data_and_picture = \
        [[_write_table_identification(identification_data),
          table_picture_place,
          Paragraph('''<para>&nbsp;</para>''', styles[DEFAULT_FONT])]
         ]
    _write_table_identification_main(content, identification_data_and_picture)


def write_contact_block(content, styles, applicant):
    contact_data = set_contact_data(applicant, styles)
    _write_table_contact(content, contact_data)


def get_academic_year(an_academic_year):
    return "{0}-{1}".format(an_academic_year, an_academic_year+1)


def write_secondary_education_block(content, styles, secondary_education):
    add_space_between_lines(content, styles)
    #content.append(Paragraph(_('secondary_education'), styles['Heading2']))
    content.append(Paragraph('<u>{0}</u>'.format(_('secondary_education')), styles['Heading2']))
    content.append(Paragraph('''<para><i><u>%s</u></i> %s : <strong>%s</strong> </para>'''
                             % (_('academic_year'),
                                _('diploma_year'),
                                get_academic_year(secondary_education.academic_year)),
                             styles['paragraph_bordered']))
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
        result = _("{0}_result".format(secondary_education.result.lower()))
        result = result.lower()
    label = Paragraph('''<para><i><u>%s</u></i> %s:</para>''' % (_('high_school_result_part1'),
                                                                 _('high_school_result_part2')), styles[DEFAULT_FONT])
    result_label = Paragraph('''<para><strong>%s</strong></para>''' % result, styles[DEFAULT_FONT])
    write_secondary_education_result_block(content, [[label,
                                                      result_label]])
    if secondary_education.national is True:
        add_space_between_lines(content, styles)
        institution_data = set_institution_data(secondary_education.national_institution, styles)
        _write_table_institution(content, institution_data)

        add_space_between_lines(content, styles)
        schedule_data = set_schedule_data(secondary_education.national_institution, styles)
        if schedule_data:
            _write_table_schedule(content, schedule_data)


def write_secondary_education_year_block(content, data):
    t = Table(data, COLS_WIDTH_SECONDARY_YEAR, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def write_addresses_block(content, styles, contact_address, legal_address):
    addresses = []
    address_data = []
    set_block_addresses_header(address_data, styles, _('addresses'))
    set_address_data(contact_address, styles, address_data)
    address_data.append(["{0}".format(''), ],)
    set_address_data(legal_address, styles, address_data)
    address_data.append(["{0}".format(''), ],)
    t = Table(address_data, COLS_WIDTH_CONTACT, repeatRows=1)
    t.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0.25),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]),
    )
    addresses.append([t])
    addresses.append(["{0}".format(_('postal_address_explanation'))])
    _write_table_addresses(content, addresses)


def set_identification_data(applicant, styles):
    data = []
    set_block_title_plus_line(data, styles, _('identification'))
    data.append(["{0} :".format(_('lastname')), format_string_for_display(applicant.user.last_name)],)
    data.append(["{0} :".format(_('firstname')), format_string_for_display(applicant.user.first_name)],)
    data.append(["{0} :".format(_('middle_name')), format_string_for_display(applicant.middle_name)],)
    data.append([' ', ' '],)
    data.append(["{0} :".format(_('birth_day')), format_date_for_display(applicant.birth_date)],)
    data.append(["{0} :".format(_('birth_place')), format_string_for_display(applicant.birth_place)],)
    if applicant.birth_country:
        data.append(["{0} :".format(_('birth_country')), format_string_for_display(applicant.birth_country.name)],)
    data.append([' ', ' '],)
    data.append(["{0} :".format(_('civil_status')), format_string_for_display_trans(applicant.civil_status)],)
    data.append(["{0} :".format(_('spouse_name')), format_string_for_display(applicant.spouse_name)],)
    data.append(["{0} :".format(_('children')), format_string_for_display(str(applicant.number_children))],)
    data.append([" ", " "],)
    return data


def set_contact_data(applicant, styles):
    data = []
    set_block_title_plus_line(data, styles, _('contact'))
    data.append(["{0} :".format(_('mobile')), format_string_for_display(applicant.phone_mobile)],)
    data.append(["{0} :".format(_('mail')), format_string_for_display(applicant.additional_email)],)
    data.append([" ", " "],)
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
        data.append([Paragraph('<u>{0}</u>'.format(_(address_type.lower())), styles['block_sub_title']), ],)
    data.append([" ", " "],)
    data.append(["{0} :".format(_('street')), street],)
    data.append(["{0} :".format(_('postal_code')), postal_code],)
    data.append(["{0} :".format(_('city')), city],)
    data.append(["{0} :".format(_('country')), country],)
    return data


def set_block_title(data, styles, title):
    data.append([
        Paragraph('<u>{0}</u>'.format(title), styles['block_title'])], )


def set_block_title_plus_line(data, styles, title):
    data.append([
        Paragraph('<u>{0}</u>'.format(title), styles['block_title'])], )
    data.append([
        Paragraph('', styles[DEFAULT_FONT])], )


def set_block_header(content, styles, title):
    content.append(
        Paragraph('<u>{0}</u>'.format(title), styles['block_header']))
    content.append(
        Paragraph('', styles[DEFAULT_FONT]))


def set_block_addresses_header(data, styles, title):
    data.append([
        Paragraph('<u>{0}</u>'.format(title), styles['block_title']), ])
    data.append([
        Paragraph(' ', styles[DEFAULT_FONT]), ])


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
    an_application = mdl.application.find_first_by_user(request.user)
    a_student = mdl_base.student.find_by_user(request.user)
    return build_pdf({'application': an_application,
                      'contact_address': get_person_address(an_application.applicant, 'CONTACT'),
                      'legal_address': get_person_address(an_application.applicant, 'LEGAL'),
                      'secondary_education': get_secondary_education(an_application.applicant),
                      'curriculum_studies': get_curriculum_list(an_application.applicant, ['LOCAL_UNIVERSITY',
                                                                                           'FOREIGN_UNIVERSITY',
                                                                                           'LOCAL_HIGH_EDUCATION',
                                                                                           'FOREIGN_HIGH_EDUCATION']),
                      'curriculum_others': get_curriculum_list(an_application.applicant, ['ANOTHER_ACTIVITY']),
                      'sociological_survey': get_sociological_survey(an_application.applicant),
                      'student': a_student})


def header_building(canvas, doc, custom_data):
    logo_institution = Image(settings.LOGO_INSTITUTION_URL, width=15*mm, height=20*mm)
    table_university = table_university_data(custom_data)
    table_applicant = table_applicant_data(custom_data)
    data_header = [[logo_institution, table_university, table_applicant], ]

    t_header = Table(data_header, [30*mm, 75*mm, 75*mm])

    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

    w, h = t_header.wrap(doc.width, doc.topMargin)
    t_header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)


def footer_building(canvas, doc, styles):
    pageinfo = "%s" % (_('preliminary_file'))
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
                            ''', ParagraphStyle(DEFAULT_FONT)))
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
        ''', ParagraphStyle(DEFAULT_FONT)))


def _write_table_identification(data):
    cc = []
    t = Table(data, COLS_WIDTH_IDENTIFICATION, repeatRows=1)
    t.setStyle(TABLE_STYLE_INNER_BLOCK)
    cc.append(t)
    return cc


def _write_table_identification_main(content, data):
    t = Table(data, COLS_WIDTH_IDENTIFICATION_MAIN, repeatRows=1)
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), BOX_BORDER_SIZE, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    content.append(t)


def _write_table_contact(content, data):
    t = Table(data, COLS_WIDTH_CONTACT, repeatRows=1)
    t.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0.25),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('BOX', (0, 0), (-1, -1), BOX_BORDER_SIZE, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def _write_table_addresses(content, data):

    t = Table(data, COL_MAX, repeatRows=1)
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]),
    )
    content.append(t)


def get_national_secondary_data(secondary_education, styles):
    data = []
    set_block_title(data, styles, "{0} {1}".format(_('high_school'), _('in_belgium_title')))

    national_community_str = ''
    if secondary_education.national_community:
        national_community_str = _(secondary_education.national_community)
    education_type_str = ''
    if secondary_education.education_type:
        education_type_str = secondary_education.education_type.name

    data.append(["{0} :".format(_('diploma_national_community')),
                 Paragraph('''<para><strong>%s</strong></para>''' % national_community_str, styles[DEFAULT_FONT])],)
    data.append(["{0} :".format(_('teaching_type')),
                 Paragraph('''<para><strong>%s</strong></para>''' % education_type_str, styles[DEFAULT_FONT])],)

    data.append([Paragraph('''<para><u>%s.</u></para>''' % (_('current_studies')), styles[DEFAULT_FONT]), ])
    data_current_studies = [[Paragraph('''<para>%s:</para>''' % (_('repetition')), styles[DEFAULT_FONT]),
                             Paragraph('''<para><strong>%s</strong></para>''' %
                                       (format_yes_no(secondary_education.path_repetition)), styles[DEFAULT_FONT])
                             ], [Paragraph('''<para>%s:</para>''' % (_('reorientation')),
                                           styles[DEFAULT_FONT]),
                                 Paragraph('''<para><strong>%s</strong></para>'''
                                           % (format_yes_no(secondary_education.path_reorientation)),
                                           styles[DEFAULT_FONT])
                                 ]]

    data.append(_write_table_current_studies(data_current_studies))
    return data


def write_secondary_education_national_block(content, data):
    t = Table(data, COLS_WIDTH_NATIONAL_EDUCATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
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
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    cc.append(t)
    return cc


def get_foreign_secondary_data(secondary_education, styles):
    data = []
    set_block_title(data, styles, "{0} {1}".format(_('high_school'), _('abroad')))
    international_diploma_title = ''
    if secondary_education.international_diploma:
        international_diploma_title = secondary_education.international_diploma
    international_diploma_language_str = ''
    if secondary_education.international_diploma_language:
        international_diploma_language_str = secondary_education.international_diploma_language.name
    equivalence_str = ''
    if secondary_education.international_equivalence:
        equivalence_str = _(secondary_education.international_equivalence)
    data.append(["{0} :".format('Intitulé du diplôme obtenu'),
                 Paragraph(international_diploma_title, styles['bold'])],)
    data.append(["{0} :".format('Régime linguistique dans lequel le diplôme a été obtenu'),
                 Paragraph(international_diploma_language_str, styles['bold'])],)
    data.append(["{0} :".format('Equivalence reconnue par la Communauté française de Belgique'),
                 Paragraph(equivalence_str, styles['bold'])],)
    return data


def write_secondary_education_foreign_block(content, data):
    t = Table(data, COLS_WIDTH_INTERNATIONAL_EDUCATION, repeatRows=1)
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def write_secondary_education_result_block(content, data):
    t = Table(data, COLS_WIDTH_SECONDARY_RESULT, repeatRows=1)
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ]))
    content.append(t)


def set_institution_data(education_institution, styles):
    data = []
    if education_institution:
        set_block_header_style(data, styles,
                               "<u>{0}</u> :".format(_('high_school_institute')), 'italic')
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
    t = Table(data, COL_MAX, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def write_curriculum_studies_block(content, styles, curriculum):
    add_space_between_lines(content, styles)
    set_block_header(content, styles, _('curriculum'))
    for cv in curriculum:
        data = get_curriculum_data(cv, styles)
        build_curriculum_study_block(content, data)
        add_space_between_lines(content, styles)


def get_curriculum_data(curriculum, styles):
    data = [[
        Paragraph("{0}:".format(submission.get_academic_year(curriculum.academic_year)), styles['Heading2']),
        Paragraph("{0}".format(_(curriculum.path_type)), styles['Heading2'])], [
        " "
        " "]]
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
        grade_type = curriculum.grade_type.name
    if curriculum.national_institution:
        national_institution_name = curriculum.national_institution.name
        national_institution_postal_code = curriculum.national_institution.postal_code
        national_institution_city = curriculum.national_institution.city

    data.append(["{0} :".format(_('community')),
                 Paragraph("<strong>{0}</strong>".format(_(national_education)), styles['bold'])],)
    data.append(["{0} :".format(_('domain')), Paragraph("<strong>{0}</strong>".format(domain), styles['bold'])],)
    data.append(["{0} :".format(_('studies_grade')),
                 Paragraph("<strong>{0}</strong>".format(grade_type), styles[DEFAULT_FONT])],)
    data.append(["{0} :".format(_('institution')),
                 Paragraph("<strong>{0}</strong>".format(national_institution_name), styles['bold'])],)
    data.append(["",
                 Paragraph("<strong>{0} {1}</strong>".format(national_institution_postal_code,
                                                             national_institution_city), styles['bold'])],)
    #
    #
    curriculum_result = ''
    if curriculum.result:
        curriculum_result = _(curriculum.result)
    data_curriculum_detail = []
    credits_enrolled = ""
    if curriculum.credits_enrolled:
        credits_enrolled = curriculum.credits_enrolled
    credits_obtained = ""
    if curriculum.credits_obtained:
        credits_enrolled = curriculum.credits_obtained
    data_curriculum_detail.append(["{0}:".format(_('result')),
                                   Paragraph("<strong>{0}</strong>".format(curriculum_result), styles['bold']),
                                   "{0}:".format('Crédits inscrits'),
                                   Paragraph("<strong>{0}</strong>".format(credits_enrolled), styles['bold'])])
    data_curriculum_detail.append(["{0}:".format(_('diploma')),
                                   Paragraph("<strong>{0}</strong>".format(format_yes_no(curriculum.diploma).upper()),
                                             styles['bold']),
                                   "{0}:".format('Crédits acquis'),
                                   Paragraph("<strong>{0}</strong>".format(credits_obtained), styles['bold'])])
    data.append([_write_table_curriculum_detail(data_curriculum_detail), ],)

    return data


def _write_table_curriculum_detail(data):
    cc = []
    t = Table(data, COLS_WIDTH_CURRICULUM_RESULTS, repeatRows=1)
    t.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    cc.append(t)
    return cc


def build_curriculum_study_block(content, data):
    t = Table(data, COLS_WIDTH_CURRICULUM_STUDIES, repeatRows=1)
    t.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def write_curriculum_others_block(content, styles, curriculum):
    add_space_between_lines(content, styles)
    for cv in curriculum:
        data = get_curriculum_other_data(cv, styles)
        build_curriculum_study_block(content, data)


def get_curriculum_other_data(curriculum, styles):
    data = [[
        Paragraph("{0} :".format(submission.get_academic_year(curriculum.academic_year)), styles['Heading2']),
        Paragraph("{0}".format(_(curriculum.path_type)), styles['Heading2'])], [
        " "
        " "]]
    activity_type = ''

    if curriculum.activity_type:
        activity_type = _("{0}_ACTIVITY".format(curriculum.activity_type))

    data.append(["{0} :".format(_('activity')),
                 Paragraph("<strong>{0}</strong>".format(activity_type), styles['bold'])],)
    if curriculum.activity_place:
        data.append(["{0} :".format(_('activity_place')),
                     Paragraph("<strong>{0}</strong>".format(curriculum.activity_place), styles['bold'])],)

    return data


def write_pdf_title(content, styles, an_application_type):
    line = MCLine(500)

    text_admission = ''
    if an_application_type == application_type.ADMISSION:
        text_admission = " / {0} {1}".format(_('preliminary_file'),
                                             _('of_admission'))

    enrollment_application_title = Paragraph('''<para>
                        <font size=16>%s</font>%s
                    </para>''' % (_('enrollment_application'),
                                  text_admission), styles["Normal"])
    content.append(enrollment_application_title)
    add_space_between_lines(content, styles)
    content.append(line)


def write_explanation_block(content, styles):
    add_space_between_lines(content, styles)
    enrollment_application_explanation = Paragraph('''<para>%s</para>''' % (_('enrollment_application_explanation')),
                                                   styles["Normal"])
    content.append(enrollment_application_explanation)
    attention = Paragraph('''<para>%s :</para>''' % (_('attention')), styles["Normal"])
    content.append(attention)
    enrollment_application_no_recto_verso = Paragraph('''<para>%s</para>''' % (_('no_recto_verso')), styles["red"])
    content.append(enrollment_application_no_recto_verso)
    enrollment_application_not_incomplete = Paragraph('''<para>%s</para>''' % (_('not_incomplete')), styles["red"])
    content.append(enrollment_application_not_incomplete)
    add_space_between_lines(content, styles)


def format_date_for_display(a_date):
    if a_date is None:
        return ''
    else:
        return a_date.strftime('%d/%m/%Y')


def write_secondary_education_exam_block(content, styles, secondary_education_exam, title):

    add_space_between_lines(content, styles)
    set_block_header(content, styles, _(title))
    data = []

    add_space_between_lines(content, styles)

    result = ''
    if secondary_education_exam.result:
        result = _("{0}".format(secondary_education_exam.result.lower()))
        result = result.lower()

    data.append([Paragraph('''<para><u>%s</u> %s</para>'''
                           % (_('inscription'),
                              _('to_this_exam')), styles["BodyText"])],)
    data.append([" ", ])
    data.append(["{0}: ".format(_('session')), format_date_for_display(secondary_education_exam.exam_date)])
    data.append(["{0}: ".format(_('result')), result])
    data.append(["{0}: ".format(_('establishment')), secondary_education_exam.institution])
    if secondary_education_exam.admission_exam_type:
        data.append(["{0}: ".format(_('title')), secondary_education_exam.admission_exam_type])
    data.append([" ", ])
    write_secondary_education_exam_detail_block(content, data)


def write_secondary_no_education_exam_block(content, styles, title):
    add_space_between_lines(content, styles)

    set_block_header(content, styles, _(title))

    content.append(Paragraph('''<para><u>%s</u> %s</para>'''
                             % (_('no_enrollment'), _('to_this_exam')), styles["paragraph_bordered"]))


def write_sociological_survey_block(content, styles, sociological_survey):
    content.append(PageBreak())
    add_space_between_lines(content, styles)

    set_block_header(content, styles, _('sociological_search'))
    data = []

    add_space_between_lines(content, styles)
    build_explanation(content, _('sociological_survey_explanation'), styles)

    add_space_between_lines(content, styles)
    data.append([Paragraph(_('family_situation'), styles['italic'])],)

    add_space_between_lines(content, styles)
    data.append(["{0} :".format(_('brotherhood')),
                 Paragraph(str(sociological_survey.number_brothers_sisters), styles['BodyText'])],)
    parent_data(_('father'), sociological_survey.father_is_deceased, sociological_survey.father_education,
                sociological_survey.father_profession, styles, data, _('deceased_male'))
    parent_data(_('mother'), sociological_survey.mother_is_deceased, sociological_survey.mother_education,
                sociological_survey.mother_profession, styles, data,  _('deceased_female'))
    family_data(_('student'), sociological_survey.student_professional_activity,
                sociological_survey.student_profession, styles, data)
    family_data(_('conjoint'), sociological_survey.conjoint_professional_activity,
                sociological_survey.conjoint_profession, styles, data)
    family_grandfather_data(_('paternal_grandfather'), sociological_survey.paternal_grandfather_profession, styles, data)
    family_grandfather_data(_('maternal_grandfather'), sociological_survey.maternal_grandfather_profession, styles, data)
    build_2_columns_block(content, data, COLS_WIDTH_SURVEY)


def build_explanation(content, data, styles):
    content.append(Paragraph('''<para><font size=10>%s</font></para>''' % data,
                             styles["paragraph_bordered"]))


def build_2_columns_block(content, data, cols_width):
    t = Table(data, cols_width, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def define_deceased(deceased):
    if deceased:
        return _('deceased_male')


def parent_data(title, deceased_status, education, profession,  styles, data, deceased_string):
    if deceased_status:
        data.append([Paragraph("<strong>{0}</strong> :".format(title), styles[DEFAULT_FONT]),
                     Paragraph(deceased_string, styles[DEFAULT_FONT])],)
        data.append(["",
                     Paragraph('''<para>%s :
                        <strong>%s</strong>
                    </para>''' % (_('studies'), _(education)), styles[DEFAULT_FONT])],)
    else:
        data.append([Paragraph("<strong>{0}</strong> :".format(title), styles[DEFAULT_FONT]),
                     Paragraph('''<para>%s :
                        <strong>%s</strong>
                    </para>''' % (_('studies'), _(education)), styles[DEFAULT_FONT])],)

    data.append([" ",
                 Paragraph('''<para>%s :
                        <strong>%s</strong>
                    </para>''' % (_('profession'), profession), styles[DEFAULT_FONT])
                 ],)

    return data


def family_data(title, professional_activity, profession, styles, data):
    col1 = ""
    if professional_activity is None:
        col1 = Paragraph("<strong>{0}</strong> :".format(title), styles[DEFAULT_FONT])
        col2 = ""
    else:
        col2 = Paragraph("<strong>{0}</strong> :".format(title), styles[DEFAULT_FONT])
    if professional_activity:
        data.append([col1,
                     Paragraph('''<para>%s :
                            <strong>%s</strong>
                        </para>''' % (_('professional_activity'), _(professional_activity)), styles[DEFAULT_FONT])],)
    data.append([col2,
                 Paragraph('''<para>%s :
                        <strong>%s</strong>
                    </para>''' % (_('profession'), profession), styles[DEFAULT_FONT])],)
    return data


def write_signature_block(content, styles):
    content.append(PageBreak())
    add_space_between_lines(content, styles)
    a = Image(ATTENTION_ICON_URL, width=20*mm, height=20*mm)

    set_block_header(content, styles, _('signature'))

    data1 = [[a, Paragraph('Date :', styles['BodyText']), Paragraph('Signature :', styles[DEFAULT_FONT])]]
    table_signature_attention = Table(data1, COLS_WIDTH_SIGNATURE_ATTENTION, repeatRows=1)
    data = [[Paragraph('''<para>%s <br/>%s<br/></para>''' % (_('signature_text_part1'),
                                                             _('signature_text_part2')), styles[DEFAULT_FONT])],
            [table_signature_attention]]
    t = Table(data, COL_MAX, repeatRows=1)

    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def write_card_block(content, styles):
    content.append(PageBreak())
    add_space_between_lines(content, styles)

    set_block_header(content, styles, _('access_card_order'))

    table_no_writing_here = data_no_writing_here(styles)
    table_picture_access = data_picture_access(styles)

    data = [[Paragraph('''<para>
                                %s<br/><br/>
                                %s<br/>
                                %s<br/>
                                %s<br/>
                                %s<br/>
                                %s<br/>
                                %s<br/>
                                %s<br/><br/>
                                %s<br/>
                                %s<br/>
                                %s<br/>
                                %s<br/>
                                %s<br/><br/>
                                %s<br/>
                                %s<br/><br/>
                                %s<br/>
                                %s<br/>
                              </para>''' % (_('access_card_txt_part1'),
                                            _('access_card_txt_part2'),
                                            _('access_card_txt_part3'),
                                            _('access_card_txt_part4'),
                                            _('access_card_txt_part5'),
                                            _('access_card_txt_part6'),
                                            _('access_card_txt_part7'),
                                            _('access_card_txt_part8'),
                                            _('access_card_txt_part9'),
                                            _('access_card_txt_part10'),
                                            _('access_card_txt_part11'),
                                            _('access_card_txt_part12'),
                                            _('access_card_txt_part13'),
                                            _('access_card_txt_part14'),
                                            _('access_card_txt_part15'),
                                            _('access_card_txt_part16'),
                                            _('access_card_txt_part17'),), styles[DEFAULT_FONT])],
            [table_no_writing_here], [table_picture_access]]

    t = Table(data, COL_MAX, repeatRows=1)

    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def data_no_writing_here(styles):
    d = Drawing(125, 1)
    d.add(Line(0, 0, 125, 0))
    data_no_writing = [[d, Paragraph(_('no_writing_here'), styles['BodyText']), d]]
    table_no_writing_here = Table(data_no_writing, COLS_WIDTH_SIGNATURE_ATTENTION, repeatRows=1)
    table_no_writing_here.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))
    return table_no_writing_here


def data_picture_access(styles):
    a = Image(ACCESS_PICTURE_PLACEMENT_URL, width=35*mm, height=45*mm)
    data_picture_access = [[a, Paragraph('NOMA', styles['BodyText'])]]
    table_picture_acccess = Table(data_picture_access, COLS_WIDTH_ACCESS_PICTURE, repeatRows=1)
    table_picture_acccess.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))
    return table_picture_acccess


def write_rules_block(content, styles, applicant):
    content.append(PageBreak())
    add_space_between_lines(content, styles)

    set_block_header(content, styles, _('university_rules_privacy'))
    content.append(Paragraph('''
                            <para>
                                %s<br/>%s : %s                           %s : %s
                            </para>
                            ''' % (_('undersigned'), _('lastname'),
                                   applicant.user.last_name, _('firstname'),
                                   applicant.user.first_name), styles['paragraph_bordered']))
    add_space_between_lines(content, styles)
    content.append(Paragraph('''
                            <para>
                                <strong>%s</strong><br/><br/>
                                %s <br/>
                                %s <br/>
                                %s <br/>
                                %s <br/>
                                %s <br/>
                                %s <br/><br/>
                                %s <br/><br/>
                                %s <br/>
                            </para>
                            ''' % (_('university_rules'),
                                   _('university_rules_txt_part1'),
                                   _('university_rules_txt_item1'),
                                   _('university_rules_txt_item2'),
                                   _('university_rules_txt_item3'),
                                   _('university_rules_txt_item4'),
                                   _('university_rules_txt_item5'),
                                   _('university_rules_txt_part2'),
                                   _('university_rules_txt_part3')), styles['paragraph_bordered']))
    add_space_between_lines(content, styles)
    content.append(Paragraph('''
                            <para>
                                <strong>%s</strong><br/><br/>
                                   %s <br/><br/>
                                   %s <br/><br/>
                                   %s <br/><br/>
                                   %s <br/>
                            </para>
                            ''' % (_('privacy_protection'),
                                   _('privacy_rules_txt_part1'),
                                   _('privacy_rules_txt_part2'),
                                   _('privacy_rules_txt_part3'),
                                   _('privacy_rules_txt_part4')), styles['paragraph_bordered']))

    add_space_between_lines(content, styles)
    content.append(Paragraph('''<para>
                                   %s
                                 </para>'''
                             % (_('read_approved')), styles['paragraph_bordered']))


def table_university_data(custom_data):
    style_header_text = get_style_header_text()
    style_header_text_bold = get_style_header_text_bold()
    data_university = [[Paragraph('Services des inscriptions', style_header_text_bold)],
                       [Paragraph('{0} {1}'.format(_('to_attention'),
                                                   custom_data['manager']), style_header_text)],
                       [Paragraph('{0}'.format(custom_data['address_street']), style_header_text)],
                       [Paragraph('{0}'.format(custom_data['address_city']), style_header_text)],
                       [Paragraph('{0}'.format(custom_data['address_country']), style_header_text)],
                       ]
    data_academic_year = [[Paragraph('{0} {1}'.format(_('academic_year'),
                                                      custom_data['academic_year']), style_header_text_bold)]
                          ]
    data_applicant = [[Paragraph('{0} {1} {2}'.format(_('application_of'),
                                                      custom_data['first_name'],
                                                      custom_data['last_name']), style_header_text_bold)],
                      ]
    table_university = Table(data_university, 75*mm, repeatRows=1)
    table_university.setStyle(TableStyle([
        ('RIGHTTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))
    table_academic = Table(data_academic_year, 75*mm, repeatRows=1)
    table_academic.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))
    table_applicant = Table(data_applicant, 75*mm, repeatRows=1)
    table_applicant.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))
    col2 = [[table_university],
            [table_academic],
            [table_applicant]]
    table_col2 = Table(col2, 75*mm, repeatRows=1)
    table_col2.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTTPADDING', (0, 0), (-1, -1), 0.25),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))
    return table_col2


def table_applicant_data(custom_data):
    style_header_text = get_style_header_text()
    style_header_text_bold = get_style_header_text_bold()
    table_noma = construct_grid_table_8_characters(custom_data['registration_id'],
                                                   _('registration_number'), style_header_text_bold)
    table_global = construct_grid_table_8_characters(custom_data['global_id'],
                                                     _('ID'), style_header_text_bold)

    data_applicant = [[Paragraph('Cadre réservé à l UCL', style_header_text_bold)],
                      [table_noma],
                      [Paragraph('''
                            <para>
                                &nbsp;
                            </para>
                            ''', style_header_text)],
                      [table_global],
                      [Paragraph('''
                            <para>
                                &nbsp;
                            </para>
                            ''', style_header_text)],
                      [Paragraph('{0} : <strong>{1}</strong>'.format(_('manager'),
                                                                      custom_data['manager']), style_header_text)],
                      [Paragraph('{0} : <strong>{1}</strong>'.format(_('reference_number'),
                                                                      custom_data['file_number']), style_header_text)],
                      [Paragraph('{0} : <strong>{1}</strong>'.format(_('sending_limit_date'),
                                                                      custom_data['limit_date']), style_header_text)],
                      ]

    table_picture_acccess = Table(data_applicant, 75*mm, repeatRows=1)
    table_picture_acccess.setStyle(TableStyle([

        ('RIGHTTPADDING', (0, 0), (-1, -1), 0.25),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'CENTER')]))
    return table_picture_acccess


def set_header_data(application, applicant, a_student):
    registration_id = ""
    global_id = ""
    if a_student:
        registration_id = a_student.registration_id
        global_id = a_student.person.global_id

    return {"manager": "manager",
            "address_street": "adresse rue",
            "address_city": "adresse ville",
            "address_country": "adresse pays",
            "academic_year": get_academic_year(application.offer_year.academic_year.year),
            "last_name": applicant.user.last_name.capitalize(),
            "first_name": applicant.user.first_name.capitalize(),
            "registration_id": registration_id,
            "global_id": global_id,
            "file_number": "?",
            "limit_date": format_date_for_display(application.submission_date + datetime.timedelta(days=30))}


def get_style_header_text():
    return ParagraphStyle(name='header_text', fontName=NORMAL_FONT_NAME, fontSize=8)


def get_style_header_text_bold():
    return ParagraphStyle(name='header_text_bold', fontName=BOLD_FONT_NAME, fontSize=8)


def construct_8_characters_data_table(a_label, noma_list, a_style):
    row_data = [Paragraph('{0}:'.format(a_label), a_style)]
    for a_character in noma_list:
        row_data.append((Paragraph('{0}'.format(a_character), a_style)))
        row_data.append((Paragraph('''<para>&nbsp;</para>''', a_style)))
    return [row_data]


def construct_grid_table_8_characters(a_value, a_label, a_style):
    if a_value:
        noma_list = list(a_value)
    else:
        noma_list = list("        ")
    data_noma = construct_8_characters_data_table(a_label, noma_list, a_style)

    table_noma = Table(data_noma, [13*mm, 5*mm, 1*mm, 5*mm, 1*mm, 5*mm, 1*mm, 5*mm, 1*mm, 5*mm, 1*mm, 5*mm, 1*mm, 5*mm, 1*mm, 5*mm], rowHeights=(5*mm))
    table_noma.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (1, 0), (-1, -1), 5),
        ('RIGHTTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTTPADDING', (1, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('GRID', (1, 0), (1, 0), 1, colors.black),
        ('GRID', (3, 0), (3, 0), 1, colors.black),
        ('GRID', (5, 0), (5, 0), 1, colors.black),
        ('GRID', (7, 0), (7, 0), 1, colors.black),
        ('GRID', (9, 0), (9, 0), 1, colors.black),
        ('GRID', (11, 0), (11, 0), 1, colors.black),
        ('GRID', (13, 0), (13, 0), 1, colors.black),
        ('GRID', (15, 0), (15, 0), 1, colors.black),
    ]))
    return table_noma


def write_application(content, styles, application, nationality):
    scholarship = "-"
    if application.scholarship:
        scholarship = application.scholarship_organization
    dubble_degree = "-"
    erasmus = "-"
    data = []
    set_block_header(content, styles, "{0}".format(_('enrollment_apllied'),
                                                   _('for'),
                                                   get_academic_year(application.offer_year.academic_year.year)))
    data.append([Paragraph('''<para>%s: <strong>%s</strong></para>''' % (_('study_year'),
                                                                         application.offer_year.acronym),
                           styles[DEFAULT_FONT])])
    data.append([Paragraph('''<para>
                                    <blocktable>
                                        <tr>
                                            <td>&nbsp;&nbsp;&nbsp;</td>
                                            <td><strong>%s</strong></td>
                                        </tr>
                                    </blocktable>
                                </para>''' % application.offer_year.title, styles[DEFAULT_FONT])])
    orientation = "-"
    if orientation:
        data.append([Paragraph('''<para>%s: <strong>%s</strong></para>''' % (_('orientation'),
                                                                             orientation),
                               styles[DEFAULT_FONT])])
    data.append([Paragraph('''<para>%s: <strong>%s</strong></para>''' % (_('site'),
                                                                         application.offer_year.campus.name),
                           styles[DEFAULT_FONT])])
    data_offer = [["{0}".format(_('scholarship')),
                   "{0}".format(_('dubble_degree')),
                   "{0}".format(_('erasmus'))],
                  ["{0}".format(scholarship),
                   "{0}".format(dubble_degree),
                   "{0}".format(erasmus)]
                  ]
    table_offer = Table(data_offer, [40*mm, 40*mm, 40*mm])
    table_offer.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 15),

        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    data.append([table_offer])

    data.append([Paragraph('''<para><strong>%s</strong></para>''' % (_('national_diploma_boolean')),
                           styles[DEFAULT_FONT])])
    national_diploma_boolean = _('no')
    if application.valuation_possible:
        national_diploma_boolean = _('yes')
    data.append([Paragraph('''<para>%s</para>''' % national_diploma_boolean, styles[DEFAULT_FONT])])
    national_nationality_boolean = _('no')
    if is_european(nationality):
        national_nationality_boolean = _('yes')
    data.append([Paragraph('''<para><strong>%s</strong></para>''' % (_('national_nationality_boolean')),
                           styles[DEFAULT_FONT])])
    data.append([Paragraph('''<para>%s</para>''' % national_nationality_boolean,
                           styles[DEFAULT_FONT])])

    t = Table(data, COL_MAX, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def is_european(country):
    if country:
        return country.european_union
    return False


def set_schedule_data(education_institution, styles):
    data = []
    return data


def _write_table_schedule(content, data):
    t = Table(data, COL_MAX, repeatRows=1)
    t.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def write_secondary_education_exam_detail_block(content, data):
    t = Table(data, COLS_WIDTH_SECONDARY_EXAM, repeatRows=1)
    t.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    content.append(t)


def family_grandfather_data(title, profession, styles, data):
    data.append([Paragraph("<strong>{0}</strong> :".format(title), styles[DEFAULT_FONT]),
                 Paragraph('''<para>%s :
                        <strong>%s</strong>
                    </para>''' % (_('profession'), profession), styles[DEFAULT_FONT])],)
    return data


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(211 * mm, 15 * mm + (0.2 * inch),
                             "Page %d / %d - %s" % (self._pageNumber, page_count, _('preliminary_file')))