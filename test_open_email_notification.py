# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.lockscreen.app import LockScreen
from marionette.by import By
from gaiatest.apps.email.app import Email
from gaiatest.mocks.mock_email import MockEmail
from gaiatest.utils.email.email_util import EmailUtil
from gaiatest.apps.email.regions.setup import SetupEmail
import sys,time

class TestActionOnNotification(GaiaTestCase):

    _notification_title = 'test'
    _notification_body = 'test'

    def setUp(self):
        GaiaTestCase.setUp(self)
        sys.path.append("./")
        try:
            self.testvars['email']['IMAP']
        except KeyError:
            raise SkipTest('account details not present in test variables')

        GaiaTestCase.setUp(self)
        self.connect_to_network()

    def test_lock_screen_open_email_notification(self):
        lock_screen = LockScreen(self.marionette)

        # setup IMAP account
        email = Email(self.marionette)
        email.launch()

        m = self.marionette
        
        # setup email
        imap = self.testvars['email']['IMAP']
        basic_setup = SetupEmail(self.marionette)
        #basic_setup.type_name(imap['name'])
        name_field = m.find_element(By.CSS_SELECTOR, 'section.card-setup-account-info input.sup-info-name')
        name_field.send_keys(imap['name'])
        #email.keyboard.send(imap['name'])
        #basic_setup.type_email(imap['email'])
        time.sleep(1)
        email_field = m.find_element(By.CSS_SELECTOR, 'section.card-setup-account-info input.sup-info-email')
        email_field.tap()
        #email_field.send_keys(imap['email'])
        email.keyboard.send(imap['email'])
        
        setup = email.tap_manual_setup()
        setup.type_imap_hostname(imap['imap_hostname'])
        setup.type_imap_name(imap['imap_name'])
        setup.type_imap_port(imap['imap_port'])
        
        _imap_password_locator = m.find_element(By.CSS_SELECTOR, 'section.card-setup-manual-config .sup-manual-composite-password')
        _imap_password_locator.clear()
        _imap_password_locator.send_keys(imap['password'])

        setup.type_smtp_hostname(imap['smtp_hostname'])
        setup.type_smtp_name(imap['smtp_name'])
        setup.type_smtp_port(imap['smtp_port'])
        _smtp_hostname_locator = m.find_element(By.CSS_SELECTOR, 'section.card-setup-manual-config .sup-manual-smtp-password')
        _smtp_hostname_locator.clear()
        _smtp_hostname_locator.send_keys(imap['password'])

        setup.tap_next()
        
        manual = m.find_element("css selector",'li[class="syncinterval-setting select-item"] > span[class="button icon icon-dialog"]')
        manual.tap()
        self.marionette.switch_to_frame()
        options = self.marionette.find_elements(By.CSS_SELECTOR, 'ol[class="value-selector-options-container"] > li')
        
        for li in options:
            if li.text == 'Every 5 minutes':
                li.tap()
                break
        
        for item in m.find_elements(By.CSS_SELECTOR, 'button.value-option-confirm'):
            if item.is_displayed() == True:
                item.tap()
                break
        self.apps.switch_to_displayed_app()

        setup.tap_account_prefs_next()
        setup.wait_for_setup_complete()
        setup.tap_continue()
        email.wait_for_message_list()
        
        ##########################
        
        # wait for sync to complete
        email.wait_for_emails_to_sync()

        # Touch home button to exit email app
        self.device.touch_home_button()

        # send email to active sync account
        mock_email = MockEmail(senders_email=self.testvars['email']['IMAP']['email'],
                               recipients_email=self.testvars['email']['IMAP']['email'])
        EmailUtil().send(self.testvars['email']['IMAP'], mock_email)

        self.device.lock()
        self.device.turn_screen_off()
        time.sleep(310)
        self.device.lock()
        #Click notification
        notifications = self.marionette.find_elements(By.CSS_SELECTOR, '#notifications-lockscreen-container div[class="notification"]')

        for no in notifications:
            if "Test email" in no.text:
                no.tap()
                open = self.marionette.find_element(By.CSS_SELECTOR, '#notifications-lockscreen-container span[class="button-actionable"]')
                open.tap()
                break;
        
        self.wait_for_condition(lambda m: self.apps.displayed_app.name == 'E-Mail')
        self.assertEqual(self.apps.displayed_app.name, 'E-Mail')


