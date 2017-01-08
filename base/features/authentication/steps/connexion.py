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

import logging
from time import sleep
from aloe_django import django_url

import aloe_webdriver
from aloe import around, world, before, step, after
from django.conf import settings
from django.core.management import call_command
from selenium import webdriver

logger = logging.getLogger(settings.DEFAULT_LOGGER)

@before.all
def with_browser():
    logger.info('\n\nLoad fixture\n\n')
    call_command('loaddata', 'test_user', interactive=False, verbosity=1)
    sleep(3)
    profile = webdriver.FirefoxProfile(settings.SELENIUM_FIREFOX_PROFILE_PATH)
    world.browser = webdriver.Firefox(profile)

@after.all
def close_all():
    world.browser.quit()

@step(r'I access the url "(.*)"')
def access_url(step, url):
    world.browser.get(django_url(step, url))
    sleep(1)

@step(r'I should be at url "(.*)"')
def shoudl_be_at(step, url):
    assert world.browser.current_url == django_url(step, url)