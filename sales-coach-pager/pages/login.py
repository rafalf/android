#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
from selenium.common.exceptions import TimeoutException
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pager.page import Page


class Login(Page, unittest.TestCase):

    user = ''
    password = ''

    def __init__(self, driver, config, locators):
        self.driver = driver
        self.config = config
        self.locators = locators

    def login(self):

        """ to login """
        
        el = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, self.locators['login_user'])),
                                                  message='element timed out: %s' % (self.locators['login_user']))
        el.send_keys(Login.user)

        self.driver.find_element_by_id(self.locators['login_pass']).send_keys(Login.password)
        el = self.driver.find_element_by_id('com.nineteenthmile:id/login')
        self.assertIsNotNone(el)
        action = TouchAction(self.driver)
        action.tap(el).perform()

    def attempt_login(self, force_login=False):

        """ to attempt to login
        force_login=True : force to login, if logged in, sign out first
        """

        try:
            el = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
                (By.ID, self.locators['login_user'])))
        except TimeoutException:
            el = None

        if el is not None:
            pass
        elif el is None and not force_login:
            return 'Logged in'
        else:
            self._sign_out()

        self.login()
