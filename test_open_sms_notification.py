# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.lockscreen.app import LockScreen
from marionette.by import By
from gaiatest.apps.system.app import System
import sys,time

class TestActionOnNotification(GaiaTestCase):

    _notification_title = 'test'
    _notification_body = 'test'

    def setUp(self):
        GaiaTestCase.setUp(self)
        
        sys.path.append("./")
        #sys.path.append("./tests/functional/WPA-EAP")



    def test_lock_screen_open_sms_notification(self):
        lock_screen = LockScreen(self.marionette)

        # Check if the screen is turned off
        #self.assertFalse(self.device.is_screen_enabled)

        _text_message_content = "Automated Test %s" % str(time.time())

        system = System(self.marionette)

        # Send a SMS to the device
        self.data_layer.send_sms(self.testvars['carrier']['phone_number'], _text_message_content)
        
        self.device.lock()
        self.device.turn_screen_off()
        
        lock_screen.wait_for_notification()
        
        #Click notification
        notifications = self.marionette.find_elements(By.CSS_SELECTOR, '#notifications-lockscreen-container div[class="notification"]')

        for no in notifications:
            if "Automated Test" in no.text:
                no.tap()
                open = self.marionette.find_element(By.CSS_SELECTOR, '#notifications-lockscreen-container span[class="button-actionable"]')
                open.tap()
                break;
        
        self.wait_for_condition(lambda m: self.apps.displayed_app.name == 'Messages')
        self.assertEqual(self.apps.displayed_app.name, 'Messages')


