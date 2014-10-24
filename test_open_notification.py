# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.lockscreen.app import LockScreen
from marionette.by import By
import sys,time

class TestActionOnNotification(GaiaTestCase):

    _notification_title = 'test'
    _notification_body = 'test'

    def setUp(self):
        GaiaTestCase.setUp(self)
        
        sys.path.append("./")

        self.device.lock()
        self.device.turn_screen_off()

    def test_lock_screen_open_notification(self):
        lock_screen = LockScreen(self.marionette)

        # Check if the screen is turned off
        self.assertFalse(self.device.is_screen_enabled)

        self.marionette.execute_script('new Notification("%s", {body: "%s"});'
                                       % (self._notification_title, self._notification_body))
        lock_screen.wait_for_notification()
        
        #Click notification
        notifications = self.marionette.find_elements(By.CSS_SELECTOR, '#notifications-lockscreen-container div[class="notification"]')

        for no in notifications:
            if self._notification_title in no.text:
                no.tap()
                open = self.marionette.find_element(By.CSS_SELECTOR, '#notifications-lockscreen-container span[class="button-actionable"]')
                open.tap()
                break;
        
        self.wait_for_condition(lambda m: self.apps.displayed_app.name == 'Homescreen')
        self.assertEqual(self.apps.displayed_app.name, 'Homescreen')


