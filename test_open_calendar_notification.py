# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.lockscreen.app import LockScreen
from marionette.by import By
import sys,time
from datetime import datetime, timedelta
from gaiatest.apps.calendar.app import Calendar
from gaiatest.apps.base import Base
from gaiatest.apps.system.regions.time_picker import TimePicker

class TestActionOnNotification(GaiaTestCase):

    def setUp(self):
        GaiaTestCase.setUp(self)
        
        sys.path.append("./")

    def test_lock_screen_open_calendar_notification(self):

        _seconds_since_epoch = self.marionette.execute_script("return Date.now();")
        now = datetime.fromtimestamp((_seconds_since_epoch + 60*1000*2) / 1000)

        event_title = '%s' % str(now.time())
        event_location = '%s' % str(now.time())

        base = Base(self.marionette)
        base.apps.launch('Calendar')
        
        calendar = Calendar(self.marionette)
        new_event = calendar.tap_add_event_button()
        
        # create a new event
        
        # input event title & location
        _event_title_input_locator = (By.XPATH, "//input[@data-l10n-id='event-title']")
        _event_location_input_locator = (By.XPATH, "//input[@data-l10n-id='event-location']")
        
        title_field = self.marionette.find_element(*_event_title_input_locator)
        title_field.send_keys(event_title)
        
        location_field = self.marionette.find_element(*_event_location_input_locator)
        location_field.send_keys(event_title)  
        
        # select event time
        m = self.marionette
        start = m.find_element("css selector",'span[id="start-time-locale"]')
        start.tap()
        
        current_minute = self.marionette.execute_script("var d = new Date(); return d.getMinutes()")
        current_hour   = self.marionette.execute_script("var h = new Date(); return h.getHours()")
        time_picker = TimePicker(self.marionette)
        
        # pick the event time
        num = int(current_minute)+2
        if num <58:
            for no in range(num):
                time_picker._flick_menu_up(time_picker._minutes_picker_locator)
        else:
            time_picker._flick_menu_up(time_picker._minutes_picker_locator)
                
        if int(current_hour) == 11:
            time_picker.spin_hour24()
            
        if int(current_hour) == 12:
            for no in range(11):
                time_picker._flick_menu_up(time_picker._hour_picker_locator)
        else:
            time_picker._flick_menu_down(time_picker._hour_picker_locator)

        for item in m.find_elements("css selector",'button.value-selector-confirm'):
            if item.is_displayed() == True:
                item.tap()
        self.apps.switch_to_displayed_app()
        
        # select the remind me timing
        _select_timing_locator = (By.CSS_SELECTOR, 'span[class="button icon icon-dialog"] > select[name="alarm[]"]')
        self.wait_for_element_displayed(*_select_timing_locator)        
        display_item = self.marionette.find_element(*_select_timing_locator)
        self.marionette.execute_script("arguments[0].scrollIntoView(false);", [display_item])
        display_item.tap()
        
        #switch to frame
        self.marionette.switch_to_frame()
        options = self.marionette.find_elements(By.CSS_SELECTOR, 'ol[class="value-selector-options-container"] > li')
        
        for li in options:
            if li.text == 'At time of event':
                li.tap()
                break
        
        for item in m.find_elements(By.CSS_SELECTOR, 'button.value-option-confirm'):
            if item.is_displayed() == True:
                item.tap()
        self.apps.switch_to_displayed_app()
        
        # save the event
        event_start_date_time = new_event.tap_save_event()
        
        # wait for event pop-up
        self.device.lock()
        self.device.turn_screen_off()
        
        #lock_screen = LockScreen(self.marionette)
        self.wait_for_element_displayed(By.CSS_SELECTOR, '#notifications-lockscreen-container > div.notification', timeout=120)
        
        #Click notification
        notifications = self.marionette.find_elements(By.CSS_SELECTOR, '#notifications-lockscreen-container div[class="notification"]')

        for no in notifications:
            if event_title in no.text:
                no.tap()
                open = self.marionette.find_element(By.CSS_SELECTOR, '#notifications-lockscreen-container span[class="button-actionable"]')
                open.tap()
                break;
        
        self.wait_for_condition(lambda m: self.apps.displayed_app.name == 'Calendar')
        self.assertEqual(self.apps.displayed_app.name, 'Calendar')
