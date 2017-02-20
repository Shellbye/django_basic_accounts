# -*- coding: utf-8 -*-
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium.webdriver.firefox.webdriver import WebDriver

import constants


class AccountsTests(StaticLiveServerTestCase):
    fixtures = []

    @classmethod
    def setUpClass(cls):
        super(AccountsTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        cls.selenium.quit()
        super(AccountsTests, cls).tearDownClass()

    def test_user_register(self):
        self.selenium.maximize_window()
        self.selenium.get("{0}{1}".format(self.live_server_url,
                                          reverse("accounts:register")))
        username_input = self.selenium.find_element_by_id("id_username")
        password_input = self.selenium.find_element_by_id("id_password")
        email_input = self.selenium.find_element_by_id("id_email")
        username_input.send_keys("i_am_test_user")
        password_input.send_keys("i_am_password")
        email_input.send_keys("shellbye@foxmail.com")
        if constants.USE_CAPTCHA:
            captcha_input = self.selenium.find_element_by_id("id_captcha_1")
            captcha_input.send_keys("PASSED")
        self.selenium.find_element_by_tag_name("form").submit()
        self._test_user_login()

    def _test_user_login(self):
        self.selenium.get("{0}{1}".format(self.live_server_url,
                                          reverse("accounts:login")))
        username_input = self.selenium.find_element_by_id("id_username")
        password_input = self.selenium.find_element_by_id("id_password")
        username_input.send_keys("i_am_test_user")
        password_input.send_keys("i_am_password")
        if constants.USE_CAPTCHA:
            captcha_input = self.selenium.find_element_by_id("id_captcha_1")
            captcha_input.send_keys("PASSED")
        self.selenium.find_element_by_tag_name("form").submit()
        self._test_update_detail()

    def _test_update_detail(self):
        self.selenium.get("{0}{1}".format(self.live_server_url,
                                          reverse("accounts:detail")))
        username_input = self.selenium.find_element_by_id("id_username")
        email_input = self.selenium.find_element_by_id("id_email")
        username_input.send_keys("i_am_test_user_edit")
        email_input.clear()
        email_input.send_keys("shellbye@qq.com")
        self.selenium.find_element_by_tag_name("form").submit()

    def _test_user_change_password(self):
        self.selenium.get("{0}{1}".format(self.live_server_url,
                                          reverse("accounts:change_pwd")))
        id_old_password = self.selenium.find_element_by_id("id_old_password")
        id_new_password = self.selenium.find_element_by_id("id_new_password")
        id_new_password_2 = self.selenium.find_element_by_id("id_new_password_2")
        id_old_password.send_keys("i_am_password")
        id_new_password.send_keys("i_am_password_new")
        id_new_password_2.send_keys("i_am_password_new")
        self.selenium.find_element_by_tag_name("form").submit()
        self._test_user_logout()

    def _test_user_logout(self):
        self.selenium.get("{0}{1}".format(self.live_server_url,
                                          reverse("accounts:logout")))



