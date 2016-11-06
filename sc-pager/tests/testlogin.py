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

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

from pager.utils import reader
from pager.utils import desiredcapabilities


from pager.pages.login import Login


class TestLogin(unittest.TestCase):

    def __init__(self, test):

        self.conf = reader.get_conf()
        self.locators = reader.get_locators()
        self.screen_saver = self.conf['screen_saver']

        self.screen_path = os.path.join(self.screen_saver, self.__class__.__name__, 'testRun-' +
                                        time.strftime("%d.%m.%y.-%H.%M", time.gmtime()))
        if not os.path.exists(self.screen_path):
            os.mkdir(self.screen_path)

        super(TestLogin, self).__init__(test)
    
    def setUp(self):
        
        desired_capabilities = desiredcapabilities.get_capabilities(self.conf['apk_dir'])
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities)
        
    def tearDown(self):
        self.driver.quit()

    def testLogin(self):

        login = Login(self.driver, self.conf, self.locators)

        login.user = self.conf['employee']
        login.password = self.conf['pass']
        login.login()

        login.save_screen(self.screen_path, 'TOAST_LOGIN_{0}.png' )

        login.assertLoginPanel()


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestLogin("testLogin"))
    runner = unittest.TextTestRunner()
    runner.run(suite)