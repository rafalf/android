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
import time
from selenium.common.exceptions import NoSuchElementException

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os


class Page(unittest.TestCase):

    def __init__(self, driver, config, locators):
        self.driver = driver
        self.config = config
        self.locators = locators

    def save_screen(self, folder_name, file_name, ocr=False, count=3):

        for i in range(count):
            self.driver.save_screenshot(os.path.join(folder_name, file_name.format(i)))
            time.sleep(0.5)

        if ocr:
            pass

    def _sign_out(self):

        """ to sign out from app """

        action = TouchAction(self.driver)

        el = self.driver.find_element_by_accessibility_id('Menu_button')
        action.tap(el).perform()

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.ID, self.locators['logout_icon'])), message='logout locator timed out')
        action.tap(el).perform()

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, self.locators['login_user'])),
                                             message='element timed out: %s' % (self.locators['login_user']))
