#!/usr/bin/env python

import unittest
import time

from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import confreader
import os

SLEEPY_TIME_DOWNLOAD = 30  # time to allow app to download resources and data
SLEEPY_TIME_LOGIN = 60     # time to allow app to login, servers are responding poorly for me.
SCREEN_SIZE = '480x800'


class TestsDemo(unittest.TestCase):

    def __init__(self, test):

        self.conf = confreader.get_conf()
        self.screen_saver = self.conf['screen_saver']
        self.coords_12 = self.conf['coords_12_{0}'.format(SCREEN_SIZE)].split(',')

        # screenshots
        self.screen_path = os.path.join(self.screen_saver, self.__class__.__name__ + '_' +
                                        time.strftime("%H%M%d%m%y", time.localtime()))
        if not os.path.exists(self.screen_path):
            os.mkdir(self.screen_path)

        super(TestsDemo, self).__init__(test)

    def setUp(self):
        
        desired_capabilities = {
        'platformName': 'Android',
        'platformVersion': '5.1.1',
        'deviceName': 'Android Emulator',
        'app': self.conf['app'],
        'newCommandTimeout': 240,
        'noReset': True
        }
        
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities)

    def tearDown(self):
        self.driver.quit()

    def test_prep(self):

        """ this is not a real test, it's the clean up method to restore clean user profile
        w/t any leads/activities. run this test if you need to to clean activities and leads up
        """

        self._login_routine(self.conf['employee'], self.conf['password'], force_login=True)
        self._delete_all_activities()
        self._navigate_to_leads_routine()
        self._delete_all_leads()
        self._sign_out()

        self._login_routine(self.conf['manager'], self.conf['password'], force_login=True)
        time.sleep(10)  # make sure it's all downloaded. sometimes server is very slow. increase if needed
        self._delete_all_activities()
        self._navigate_to_leads_routine()
        self._delete_all_leads()
        self._sign_out()

    def test_android_001(self):

        """ MUST BE SIGNED OUT !"""

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
            (By.ID, 'com.nineteenthmile:id/edit_username')), message='Login panel not present')

        self.driver.find_element_by_id('com.nineteenthmile:id/edit_username').send_keys(self.conf['employee'])
        self.driver.find_element_by_id('com.nineteenthmile:id/edit_password').send_keys(self.conf['password'] + '_')

        el = self.driver.find_element_by_id('com.nineteenthmile:id/login')
        action = TouchAction(self.driver)
        action.tap(el).perform()

        for i in range(3):
            self.driver.save_screenshot(os.path.join(self.screen_path, 'ERROR_LOGIN_TOAST{0}.png'.format(i)))
            time.sleep(0.5)

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
            (By.ID, 'com.nineteenthmile:id/edit_username')), message='Login panel not present')
     
    def test_android_002_003_004(self):

        self._login_routine(self.conf['employee'], self.conf['password'])

        # /// set up -  delete leads ///

        # delete leads & activities
        self._delete_all_activities()
        self._navigate_to_leads_routine()
        self._delete_all_leads()
        self._navigate_to_planner_routine()

        action = TouchAction(self.driver)

        # /// start the actual test ///

        # tap on add
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('Add_new'))
        action.tap(el).perform()

        # tap on choose person
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('choose_person'))
        action.tap(el).perform()

        # tap on contact - top
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView1')))
        tapped_name = el.text
        action.tap(el).perform()

        # verify name
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('choose_person'))
        chosen_person = el.text

        self.assertEqual(tapped_name, chosen_person)

        self._activity_routine('ACTIVITY', 'creating activity note')

        # 003 test
        #

        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('dsr_button'))
        action.tap(el).perform()

        # x and view
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_titleBar_textView_cancel')))
        self.driver.find_element_by_id('com.nineteenthmile:id/dsr_main_page_textView_answer2')

        # fill DSR
        el = self.driver.find_element_by_id('com.nineteenthmile:id/dsr_main_page_textView_answer1')
        action.tap(el).perform()

        # tap on meeting
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/list_dsr_activities_textView_header')))

        # verify name
        if not el.text.count(tapped_name):
            self.fail('name incorrect: %s != %s' % (el.text, tapped_name))

        action.tap(el).perform()

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_review_textView_step')))
        self.assertEqual(el.text, 'Step 1 of 5')

        # 30 mins
        el = self.driver.find_element_by_id('com.nineteenthmile:id/dsr_review_step2_textView_answer2')
        action.tap(el).perform()

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_review_textView_step')))
        self.assertEqual(el.text, 'Step 2 of 5')

        el = self.driver.find_element_by_accessibility_id('follow_yes')
        action.tap(el).perform()

        self._activity_routine('DSR')

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_review_textView_step')))
        self.assertEqual(el.text, 'Step 3 of 5')

        # notes
        el = self.driver.find_element_by_accessibility_id('dsr_notes')
        el.send_keys('NOTES')  # send keys
        self.driver.hide_keyboard()

        # right to left
        self.driver.swipe(400, 200, 100, 200, 800)

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_review_textView_step')))
        self.assertEqual(el.text, 'Step 4 of 5')

        # yes
        el = self.driver.find_element_by_accessibility_id('status_yes')
        action.tap(el).perform()

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/custom_dialog_dsr_step4_textView_question')))
        self.assertEqual(el.text, 'No lead added. Would you like to add a new lead?')

        # yes
        el = self.driver.find_element_by_id('com.nineteenthmile:id/custom_dialog_dsr_step4_textView_textView_answer1')
        action.tap(el).perform()

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lead_wizard_textView_title')))
        self.assertEqual(el.text, 'Add Lead')

        # right to left
        # self.driver.save_screenshot(os.path.join(self.screen_path, "SWIPE_ADD_LEAD.png")) # for coordinates
        self.driver.swipe(400, 400, 50, 400, 800)
        time.sleep(2)

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lw_step2_textView_source1')))
        action.tap(el).perform()

        self._add_product_routine()

        # right to left
        # self.driver.save_screenshot(os.path.join(self.screen_path, "SWIPE_DETAILS.png")) # for coordinates
        self.driver.swipe(400, 500, 50, 500, 1500)
        time.sleep(2)

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lead_wizard_textView_subheader_text')))
        self.assertEqual(el.text, 'Review Lead Details')

        self._add_notes_routine('Notes for Lead Details')

        # review details
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_review_step5_textView_heading')))

        self.driver.save_screenshot(os.path.join(self.screen_path, "REVIEW_DETAILS.png"))

        # save
        el = self.driver.find_element_by_id('com.nineteenthmile:id/dsr_review_titleBar_textView_done')
        action.tap(el).perform()

        # DSR
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_titleBar_textView_title')))

        self.driver.save_screenshot(os.path.join(self.screen_path, "TOP_ACTIVITY_GREEN.png"))

        # close
        el = self.driver.find_element_by_id('com.nineteenthmile:id/dsr_titleBar_textView_cancel')
        action.tap(el).perform()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dsr_main_page_textView_question')))

        # close
        el = self.driver.find_element_by_id('com.nineteenthmile:id/dsr_titleBar_textView_cancel')
        action.tap(el).perform()

        # expand
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/scroll_text_header')))
        action = TouchAction(self.driver)
        action.tap(el).perform()

        # test 04
        #
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/panelSettings')))  # displaying

        self.driver.save_screenshot(os.path.join(self.screen_path, "TOP_ACTIVITY_COMPLETED.png"))

        self.driver.swipe(400, 350, 50, 350, 800)

        time.sleep(1)
        self.driver.save_screenshot(os.path.join(self.screen_path, "TOP_ACIVITY_PENDING.png"))

        # self._sign_out()

    def test_android_005_007(self):

        """ adding a lead
            lead stage    """

        self._login_routine(self.conf['employee'], self.conf['password'])

        # /// set up -  delete leads ///

        # delete leads
        self._navigate_to_leads_routine()
        self._delete_all_leads()
        self._navigate_to_planner_routine()

        action = TouchAction(self.driver)

        # /// start the actual test ///

        self._navigate_to_leads_routine()

        # ( + )
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lead_imageButton_add')))
        action.tap(el).perform()

        # tap on contact
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('add_contact'))
        action.tap(el).perform()

        # tap on contact - top
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView1')))
        tapped_name = el.text
        action.tap(el).perform()

        # verify selected contact
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('add_contact'))
        self.assertEqual(el.text, tapped_name)  # verify tapped name

        # self.driver.save_screenshot(os.path.join(self.screen_path, "SWIPE_ADD_LEAD.png")) # 4 coordinates
        self.driver.swipe(400, 400, 50, 400, 800)

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lw_step2_textView_source1')))
        action.tap(el).perform()

        self._add_product_routine()

        # self.driver.save_screenshot(os.path.join(self.screen_path, "SWIPE_LEAD_DETAILS.png")) # 4 coordinates
        self.driver.swipe(400, 500, 100, 500, 800)

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lead_wizard_textView_subheader_text')))
        self.assertEqual(el.text, 'Review Lead Details')

        self._add_notes_routine()

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_planner')))
        self.assertEqual(el.text, 'Leads')

        el = self.driver.find_elements_by_id('com.nineteenthmile:id/divider')
        if len(el) != 1:
            self.fail('One lead and only one lead must be present. 1 != %d' % len(el))

        el = self.driver.find_element_by_id('com.nineteenthmile:id/divider')
        action.tap(el).perform()

        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lead_details_textView')))

        # contacted
        el = self.driver.find_element_by_id('com.nineteenthmile:id/lead_details_textView_lead_stage3')
        action.tap(el).perform()

        # save
        el = self.driver.find_element_by_id('com.nineteenthmile:id/lead_details_button_done')
        action.tap(el).perform()

        # leads
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_planner')))

        el = self.driver.find_elements_by_id('com.nineteenthmile:id/divider')
        if len(el) != 0:
            self.fail('Lead moved to prospects. 0 != %d' % len(el))

        # contacted
        el = self.driver.find_element_by_id('com.nineteenthmile:id/textView_contacted')
        action.tap(el).perform()

        # moved to contacted
        el = self.driver.find_elements_by_id('com.nineteenthmile:id/divider')
        if len(el) != 1:
            self.fail('One lead and only one lead must be present. 1 != %d' % len(el))

    def test_android_006(self):

        """ manager """

        action = TouchAction(self.driver)

        self._login_routine(self.conf['manager'], self.conf['password'], force_login=True)

        el = WebDriverWait(self.driver, 10).until(lambda y: self.driver.find_element_by_accessibility_id('team'))
        action.tap(el).perform()

        self._navigate_to_leads_routine()

        # must have a lead
        lead_found = None
        tabs = ['com.nineteenthmile:id/textView_prospect', 'com.nineteenthmile:id/textView_contacted', 'com.nineteenthmile:id/textView_proposal_given', 'com.nineteenthmile:id/textView_in_negtiation']
        for tab in tabs:   # prospects, contacted and so on ...
            els_tab = self.driver.find_element_by_id(tab)
            action.tap(els_tab).perform()

            els = self.driver.find_elements_by_id('com.nineteenthmile:id/divider')  # leads
            if len(els) != 0:
                lead_found = True
                break # lead found

        self.assertIsNotNone(lead_found, msg='Lead not found. Must have at least one lead created before test starts')

        action.long_press(els[0]).perform()

        # assign
        el = WebDriverWait(self.driver, 10).until(lambda y: self.driver.find_element_by_accessibility_id('assign'))
        action.tap(el).perform()

        # assign to myself ( Test Manager )
        els = WebDriverWait(self.driver, 10).until(lambda y: self.driver.find_elements_by_id('com.nineteenthmile:id/textView1'))
        for el in els:
            if el.text == 'TestManager':
                break

        self.assertEqual('TestManager',el.text)
        action.tap(el).perform()

        # click on Yes
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/confirm_assign_yes')))
        action.tap(el).perform()

        self.driver.save_screenshot(os.path.join(self.screen_path, "REASSIGNED.png"))

        self._navigate_to_planner_routine()

        # 1 lead reassigned
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/scroll_text_Closures_count')))

        self.assertEqual(el.text, '(1)')

        self._sign_out()

    def test_android_008(self):

        """ add channel partner """

        action = TouchAction(self.driver)

        self._login_routine(self.conf['employee'], self.conf['password'])

        self._navigate_to_channel_partner_routine()

        # ( + )
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/rp_imageButton_add')))
        action.tap(el).perform()

        # add channel
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/custom_dialog_agent_textView_answer1')))
        action.tap(el).perform()

        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/agent_wizard_textView_title')))
        self.assertEqual(el.text, 'Add New')

        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/add_agent_name')))
        action.tap(el).perform()

        text_channel = 'Add channel partner ' + time.strftime("%H:%M:%S", time.localtime())
        el.send_keys(text_channel)
        self.driver.hide_keyboard('Done')

        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/add_agent_phone')))
        action.tap(el).perform()

        el.send_keys('0123456')
        self.driver.hide_keyboard('Done')

        self.driver.swipe(400, 400, 50, 400, 800)
        time.sleep(2)

        # step 2 of 4
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/agent_wizard_textView_header_value')))
        self.assertEqual(el.text, '2')

        self.driver.swipe(400, 400, 50, 400, 800)
        time.sleep(1)

        self.driver.save_screenshot(os.path.join(self.screen_path, "EXPERIENCE_TOAST.png"))

        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/add_agent_experience')))
        action.tap(el).perform()

        # no
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/experience_value2')))
        action.tap(el).perform()

        self.driver.swipe(400, 400, 50, 400, 800)
        time.sleep(1)

        # step 3 of 4
        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/agent_wizard_textView_header_value')))
        self.assertEqual(el.text, '3')

        self.driver.swipe(400, 400, 50, 400, 800)
        time.sleep(1)

        self.driver.save_screenshot(os.path.join(self.screen_path, "CLOSE_DATE_TOAST.png"))

        self.driver.swipe(100, 400, 100, 100, 800)

        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/txt_enter_clouser_date')))
        action.tap(el).perform()

        self._tap_today_and_ok()

        self.driver.swipe(400, 400, 50, 400, 800)
        time.sleep(1)

        el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/agent_wizard_button_done')))
        action.tap(el).perform()

        els = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, 'com.nineteenthmile:id/textView_pipeline_list_content1')))

        self.driver.save_screenshot(os.path.join(self.screen_path, "CHANNEL_CREATED.png"))

        texts = [el.text for el in els]
        self.assertIn(text_channel, texts)

    #  ----------------
    #  ----------------

    def _login_routine(self, user, password, force_login=False):

        """ to attempt login
            use force_login to force to login e.g. if logged in already
            sign out and then login
        """

        # wait for app and login

        try:
            el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/edit_username')))
        except:
            el = None

        if el is not None:
            pass
        elif el is None and not force_login:
            return 'Logged in'
        else:
            el = self._sign_out()

        self.assertIsNotNone(el)

        el.send_keys(user)
        self.driver.find_element_by_id('com.nineteenthmile:id/edit_password').send_keys(password)

        el = self.driver.find_element_by_id('com.nineteenthmile:id/login')
        action = TouchAction(self.driver)
        action.tap(el).perform()

        WebDriverWait(self.driver, SLEEPY_TIME_LOGIN).until(EC.presence_of_element_located(
            (By.ID, 'com.nineteenthmile:id/planner_button_dsr')), message='did not login in time. try to increase: SLEEPY_TIME_LOGIN')

        # let it download
        time.sleep(SLEEPY_TIME_DOWNLOAD)

    def _navigate_to_leads_routine(self):

        """ navigate to leads from main panel """

        action = TouchAction(self.driver)

        el = self.driver.find_element_by_accessibility_id('Menu_button')
        action.tap(el).perform()

        # leads
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_drawer')))

        els = self.driver.find_elements_by_id('com.nineteenthmile:id/textView_drawer')
        for el in els:
            if el.text == 'Leads':
                action.tap(el).perform()
                break

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_planner')))
        self.assertEqual(el.text, "Leads")

    def _navigate_to_channel_partner_routine(self):

        """ navigate to channel partner from main panel """

        action = TouchAction(self.driver)

        el = self.driver.find_element_by_accessibility_id('Menu_button')
        action.tap(el).perform()

        # leads
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_drawer')))

        els = self.driver.find_elements_by_id('com.nineteenthmile:id/textView_drawer')
        for el in els:
            if el.text == 'Channel Partner':
                action.tap(el).perform()
                break

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_planner')))
        self.assertEqual(el.text, "Channel Partner")

    def _sign_out(self):

        """ to sign out from app """

        action = TouchAction(self.driver)
        
        el = self.driver.find_element_by_accessibility_id('Menu_button')
        action.tap(el).perform()
        
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/logout_view_logout_icon')))
        action.tap(el).perform()
        
        el = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/edit_username')))

        return el

    def _delete_all_leads(self):
        
        """ delete all leads """
        
        action = TouchAction(self.driver)
        
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_planner')))
        self.assertEqual(el.text, "Leads")

        tabs = ['com.nineteenthmile:id/textView_prospect', 'com.nineteenthmile:id/textView_contacted', 'com.nineteenthmile:id/textView_proposal_given', 'com.nineteenthmile:id/textView_in_negtiation']
        for tab in tabs:   # prospects, contacted and so on ...
            els_tab = self.driver.find_element_by_id(tab)
            action.tap(els_tab).perform()

            els = self.driver.find_elements_by_id('com.nineteenthmile:id/divider')  # leads
            while els:
                for __ in els:
                    el = self.driver.find_element_by_id('com.nineteenthmile:id/divider')
                    action.long_press(el=el, duration=2000).perform()
                    el = WebDriverWait(self.driver, 10).until(lambda y: self.driver.find_element_by_accessibility_id('delete'))
                    action.tap(el).perform()
                    el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/custom_dialog_swipe_answer1')))
                    action.tap(el).perform()
                els = self.driver.find_elements_by_id('com.nineteenthmile:id/divider')
            
    def _delete_all_activities(self):
        
        """ function to delete all activities """

        action = TouchAction(self.driver)  
        
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/scroll_text_header_count')))
        if el.text != '(0)':
            #expand
            el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/scroll_text_header')))
            action.tap(el).perform()
        
            el = self.driver.find_element_by_id('com.nineteenthmile:id/textView_name')
            action.long_press(el=el, duration=2000).perform()

            el_chck = WebDriverWait(self.driver, 10).until(
                lambda y: self.driver.find_element_by_accessibility_id('select_all'))
            action.tap(el_chck).perform()
            el = WebDriverWait(self.driver, 10).until(lambda y: self.driver.find_element_by_accessibility_id('delete'))
            action.tap(el).perform()
            el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/custom_dialog_swipe_answer1')))
            action.tap(el).perform()
            time.sleep(1)

            # collapse
            el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/scroll_text_header')))
            action.tap(el).perform()

    def _navigate_to_planner_routine(self):

        action = TouchAction(self.driver)
        
        el = self.driver.find_element_by_accessibility_id('Menu_button')
        self.assertIsNotNone(el)
        action.tap(el).perform()
        
        # leads
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_drawer')))
        
        els = self.driver.find_elements_by_id('com.nineteenthmile:id/textView_drawer')
        for el in els:
            if el.text == 'Planner':
                action.tap(el).perform()
                break
                
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/textView_planner')))
        self.assertEqual(el.text, "Planner")

    def _activity_routine(self, screenshot_err, notes='activity routine notes'):
        
        action = TouchAction(self.driver)
        
        # tap on purpose 
        el = WebDriverWait(self.driver, 10).until(lambda y: self.driver.find_element_by_accessibility_id('select_purpose'))
        action.tap(el).perform()
          
        # tap on top 1
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/meeting_purpose1')))
        tapped_name = el.text
        action.tap(el).perform()
          
        # verify purpose
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('select_purpose'))
        chosen_purpose = el.text
          
        self.assertEqual(tapped_name, chosen_purpose)
          
        # tap on date 
        el = self.driver.find_element_by_accessibility_id('choose_expected_close_date')
        action.tap(el).perform()
          
        self._tap_today_and_ok()
          
        today = time.strftime("%d %b, %Y", time.localtime())
        el = self.driver.find_element_by_accessibility_id('choose_expected_close_date')
        self.assertEqual(el.text, today)
          
        # tap on save
        el = self.driver.find_element_by_id('com.nineteenthmile:id/button_done')
        action.tap(el).perform()

        # appium is too slow
        # for i in range(3):
        #     self.driver.save_screenshot(os.path.join(self.screen_path, "TIME_%s_TOAST_%d.png" % (screenshot_err, i)))
        #     time.sleep(0.5)
         
        # tap on choose time
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('choose_time'))
        action.tap(el).perform()

        # tap on time: hours ( to type: 12)
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/time_picker')))
        action.tap(el, self.coords_12[0], self.coords_12[1]).perform()
        action.long_press(x=self.coords_12[0], y=self.coords_12[1], duration=500).perform()
         
        time.sleep(2)
        
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/minutes')))
        action.tap(el).perform()
         
        # minutes 
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/time_picker')))
        action.tap(el, self.coords_12[0], self.coords_12[1]).perform()
        action.long_press(x=self.coords_12[0], y=self.coords_12[1], duration=500).perform()
         
        time.sleep(1)

        # tap ok
        el = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/ok')))
        action.tap(el).perform()

        # xpath not helping, the same behaviour
        # el = self.driver.find_element_by_xpath("//android.widget.Button[@text='OK']")
        # action.tap(el).perform()
         
        # activity panel  (should be checking for: 12:00 - appium 1.4, failing in appium 1.6 )
        # https://github.com/appium/appium/issues/7127
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id('choose_time'))
        if not el.text.count('12:00'):
            self.fail('time incorrect: %s' % el.text)
        
        self.driver.swipe(100, 400, 100, 100, 800)
         
        # notes
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/editText')))
        action.tap(el).perform()
        el.send_keys(notes)  # send keys
        self.driver.hide_keyboard('Done')

        # tap on save
        el = self.driver.find_element_by_id('com.nineteenthmile:id/button_done')
        action.tap(el).perform()

    def _add_product_routine(self, amount='10'):
        
        action = TouchAction(self.driver)

        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lead_wizard_textView_subheader_text')))
        self.assertEqual(el.text, 'Add Product Details')
         
        el = self.driver.find_element_by_id('com.nineteenthmile:id/lw_step3_textView_addProduct')
        action.tap(el).perform()
 
        # select product
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/dialog_list_view')))
        action.tap(el).perform()
         
        el = self.driver.find_element_by_id('com.nineteenthmile:id/txt_enter_amount')
        el.send_keys(amount)
         
        el = self.driver.find_element_by_id('com.nineteenthmile:id/txt_enter_clouser_date')
        action.tap(el).perform()
         
        self._tap_today_and_ok()
         
        # save
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/button_product_done')))
        action.tap(el).perform()
         
        # product added
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/product_name')))
    
    def _add_notes_routine(self, notes='blablabla'):
        
        action = TouchAction(self.driver)
        # up swipe
        self.driver.swipe(100, 400, 100, 100, 800)
          
        # notes
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lw_step4_add_notes')))
        action.tap(el).perform()
        el.send_keys(notes)  
        self.driver.hide_keyboard('Done')
          
        el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'com.nineteenthmile:id/lead_wizard_button_done'))) 
        action.tap(el).perform()      

    def _tap_today_and_ok(self):
        
        # tap on today
        today = time.strftime("%d %B %Y", time.localtime())
        el = WebDriverWait(self.driver, 10).until(lambda function: self.driver.find_element_by_accessibility_id(today + ' selected'))
        action = TouchAction(self.driver)
        action.tap(el).perform()
          
        # tap on OK 
        el = self.driver.find_element_by_id('com.nineteenthmile:id/ok')
        action.tap(el).perform()

if __name__ == "__main__":
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestsDemo)
    # unittest.TextTestRunner(verbosity=2).run(suite)
    
    suite = unittest.TestSuite()
    suite.addTest(TestsDemo("test_prep"))
    suite.addTest(TestsDemo("test_android_001"))
    suite.addTest(TestsDemo("test_android_002_003_004"))
    suite.addTest(TestsDemo("test_android_005_007"))
    suite.addTest(TestsDemo("test_android_006"))
    suite.addTest(TestsDemo("test_android_008"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

